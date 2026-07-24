import asyncio
import os
import threading
import time
from typing import Optional, List, Callable
import pyaudio
from pydub import AudioSegment
from datetime import datetime


class AudioRecorder:
    """Handles audio recording with triple-stream pattern."""

    def __init__(self, snowflake_manager):
        self.snowflake_manager = snowflake_manager
        self.pyaudio_instance = None
        self.is_recording = False
        self.recording_threads = []
        self._upload_semaphore = threading.Semaphore(3)  # max 3 concurrent uploads

        # Audio configuration (optimized to prevent overflow)
        self.sample_rate = 44100
        self.channels = 1  # Mono
        self.format = pyaudio.paInt16
        self.chunk_size = 2048
        self.segment_duration = 10  # seconds

        # Storage paths
        self.temp_dir = "temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Callback for real-time updates
        self.update_callback: Optional[Callable] = None

        # Recording state
        self.current_meeting_id: Optional[str] = None
        self.archive_filename: Optional[str] = None
        self.chunk_counter = 0
        self.chunk_lock = threading.Lock()

    def is_available(self) -> bool:
        """Check if audio recording is available."""
        try:
            if not self.pyaudio_instance:
                self.pyaudio_instance = pyaudio.PyAudio()
            device_count = self.pyaudio_instance.get_device_count()
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return True
            return False
        except Exception as e:
            print(f"Audio not available: {str(e)}")
            return False

    def get_input_devices(self) -> List[dict]:
        """Get list of available input devices."""
        devices = []
        try:
            if not self.pyaudio_instance:
                self.pyaudio_instance = pyaudio.PyAudio()
            device_count = self.pyaudio_instance.get_device_count()
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'max_input_channels': device_info['maxInputChannels'],
                        'default_sample_rate': device_info['defaultSampleRate']
                    })
        except Exception as e:
            print(f"Error listing input devices: {str(e)}")
        return devices

    def _get_next_chunk_number(self):
        """Get the next chunk number in a thread-safe manner."""
        with self.chunk_lock:
            self.chunk_counter += 1
            return self.chunk_counter

    async def start_recording(self, meeting_id: str, device_index: Optional[int] = None):
        """Start triple-stream recording."""
        if self.is_recording:
            return {"error": "Recording already in progress"}

        with self.chunk_lock:
            self.chunk_counter = 0

        self.current_meeting_id = meeting_id
        self.is_recording = True

        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.archive_filename = f"{self.temp_dir}/{meeting_id}_0_{timestamp}_.mp3"

        print(f"Starting recording for meeting {meeting_id}")

        try:
            if not self.pyaudio_instance:
                self.pyaudio_instance = pyaudio.PyAudio()

            # 1. Primary stream (T+0)
            primary_thread = threading.Thread(
                target=self._record_stream,
                args=("primary", 0, device_index)
            )
            primary_thread.start()
            self.recording_threads.append(primary_thread)

            # 2. Secondary stream (T+7) — boundary overlap
            await asyncio.sleep(7)
            secondary_thread = threading.Thread(
                target=self._record_stream,
                args=("secondary", 5, device_index)
            )
            secondary_thread.start()
            self.recording_threads.append(secondary_thread)

            # 3. Archive stream (continuous)
            archive_thread = threading.Thread(
                target=self._record_archive,
                args=(device_index,)
            )
            archive_thread.start()
            self.recording_threads.append(archive_thread)

            return {"success": True, "message": "Recording started"}

        except Exception as e:
            print(f"Failed to start recording: {str(e)}")
            self.is_recording = False
            return {"error": str(e)}

    async def stop_recording(self):
        """Stop all recording streams and upload archive."""
        if not self.is_recording:
            return

        print("Stopping recording...")
        self.is_recording = False

        for thread in self.recording_threads:
            thread.join(timeout=5)
        self.recording_threads.clear()

        # Upload archive before close_meeting runs
        if self.archive_filename and os.path.exists(self.archive_filename):
            await self._upload_archive()

        print("Recording stopped")

    def _record_stream(self, stream_name: str, offset: int, device_index: Optional[int]):
        """Record segmented stream for real-time processing directly to MP3."""
        segment_count = 0
        try:
            stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )

            while self.is_recording:
                segment_count += 1
                frames = []
                frames_to_record = int(self.sample_rate / self.chunk_size * self.segment_duration)

                for _ in range(frames_to_record):
                    if not self.is_recording:
                        break
                    try:
                        data = stream.read(self.chunk_size, exception_on_overflow=False)
                        frames.append(data)
                    except Exception as e:
                        print(f"Audio read error (continuing): {e}")
                        continue

                if frames and self.is_recording:
                    chunk_num = self._get_next_chunk_number()
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                    mp3_filename = f"{self.temp_dir}/{self.current_meeting_id}_{chunk_num:03d}_{timestamp}_.mp3"
                    self._save_mp3_file(mp3_filename, frames)
                    self._schedule_upload(mp3_filename, "segment")

            stream.stop_stream()
            stream.close()

        except Exception as e:
            print(f"Error in {stream_name} recording stream: {str(e)}")

    def _record_archive(self, device_index: Optional[int]):
        """Record complete meeting archive directly as MP3."""
        frames = []
        try:
            stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )

            while self.is_recording:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"Archive audio read error (continuing): {e}")
                    continue

            stream.stop_stream()
            stream.close()

            if frames:
                self._save_mp3_file(self.archive_filename, frames)
                print(f"Archive saved: {self.archive_filename}")

        except Exception as e:
            print(f"Error in archive recording: {str(e)}")

    def _save_mp3_file(self, filename: str, frames: List[bytes]):
        """Save audio frames directly as MP3 file."""
        try:
            raw_data = b''.join(frames)
            audio = AudioSegment(
                raw_data,
                frame_rate=self.sample_rate,
                sample_width=self.pyaudio_instance.get_sample_size(self.format),
                channels=self.channels
            )
            audio.export(filename, format="mp3", bitrate="128k")
        except Exception as e:
            print(f"Error saving MP3 file: {str(e)}")

    def _schedule_upload(self, filename: str, upload_type: str):
        """Schedule upload to Snowflake without blocking the recording thread."""
        import threading

        def _do_upload():
            self._upload_semaphore.acquire()
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._upload_file_to_snowflake(filename, upload_type))
                finally:
                    loop.close()
            except Exception as e:
                print(f"Error in upload thread for {upload_type}: {str(e)}")
            finally:
                self._upload_semaphore.release()

        threading.Thread(target=_do_upload, daemon=True).start()

    async def _upload_file_to_snowflake(self, filename: str, upload_type: str):
        """Upload file to Snowflake stage, transcribe, extract, and push WebSocket update."""
        try:
            staged_path = await self.snowflake_manager.upload_mp3_to_stage(filename)
            print(f"Uploaded {upload_type} to Snowflake: {staged_path}")

            success = await self.snowflake_manager.process_audio_transcription(staged_path)
            if success:
                print(f"Transcription completed for {upload_type}")

                if self.current_meeting_id and self.update_callback:
                    transcript_chunks = await self.snowflake_manager.get_meeting_transcript(
                        self.current_meeting_id
                    )

                    await self.update_callback({
                        "type": "meeting_updated",
                        "meeting_id": self.current_meeting_id,
                        "transcript_chunks": [c['text'] for c in transcript_chunks if c['text']],
                        "timestamp": datetime.now().isoformat()
                    })

            if os.path.exists(filename):
                os.remove(filename)

        except Exception as e:
            print(f"Error uploading {upload_type} to Snowflake: {str(e)}")

    async def _upload_archive(self):
        """Upload complete meeting archive to Snowflake (transcription happens at meeting close)."""
        try:
            if not self.archive_filename or not os.path.exists(self.archive_filename):
                print("No archive file to upload")
                return

            staged_path = await self.snowflake_manager.upload_mp3_to_stage(self.archive_filename)
            print(f"Uploaded archive to Snowflake: {staged_path}")

            if os.path.exists(self.archive_filename):
                os.remove(self.archive_filename)

            if self.update_callback:
                await self.update_callback({
                    "type": "archive_uploaded",
                    "file": staged_path,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"Error uploading archive: {str(e)}")

    def set_update_callback(self, callback: Callable):
        """Set callback for real-time updates."""
        self.update_callback = callback

    def cleanup(self):
        """Clean up resources."""
        self.is_recording = False
        for thread in self.recording_threads:
            thread.join(timeout=3)
        self.recording_threads.clear()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        try:
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
        except:
            pass
