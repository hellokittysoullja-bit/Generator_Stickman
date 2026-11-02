import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import assemble_frames  # noqa: E402


def test_video_music_folder_wins_over_shared(tmp_path):
    (tmp_path / "music").mkdir()
    (tmp_path / "music" / "own.mp3").write_bytes(b"x")
    assert assemble_frames.music_file(str(tmp_path)) == str(tmp_path / "music" / "own.mp3")


def test_without_own_music_shared_track_is_used(tmp_path):
    shared = assemble_frames.music_file()
    assert assemble_frames.music_file(str(tmp_path)) == shared
