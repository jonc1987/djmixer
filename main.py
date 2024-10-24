import streamlit as st
import tempfile
from pydub import AudioSegment, effects

def enhance_audio(audio_segment, eq_type):
    audio_segment = audio_segment.normalize()  # Normalize the volume

    # Apply EQ based on the chosen type
    if eq_type == 'Dance/Electronic':
        audio_segment = audio_segment.low_pass_filter(100)  # Boost low frequencies for bass-heavy sound
        audio_segment = audio_segment.high_pass_filter(7000)  # Enhance high frequencies for clarity
    elif eq_type == 'Classical':
        audio_segment = audio_segment.low_pass_filter(800)  # Reduce bass
        audio_segment = audio_segment.high_pass_filter(1000)  # Boost mids and highs
    return audio_segment

def apply_filters(audio_segment, high_pass, low_pass):
    """ Apply high-pass and low-pass filters """
    if high_pass:
        audio_segment = audio_segment.high_pass_filter(high_pass)
    if low_pass:
        audio_segment = audio_segment.low_pass_filter(low_pass)
    return audio_segment

def process_audio(file1, file2, crossfade_duration, eq_type, cue_point1, cue_point2, volume1, volume2, high_pass=None, low_pass=None):
    # Load first audio file
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio1:
        temp_audio1.write(file1.read())
        track1 = AudioSegment.from_file(temp_audio1.name)

    # Load second audio file
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio2:
        temp_audio2.write(file2.read())
        track2 = AudioSegment.from_file(temp_audio2.name)

    # Apply cue points (if any)
    if cue_point1 > 0:
        track1 = track1[cue_point1:]
    if cue_point2 > 0:
        track2 = track2[cue_point2:]

    # Map the volume (0 to 200) to a decibel change (-30 to +6)
    db_volume1 = (volume1 - 100) / 10  # 100 is neutral, +6 dB max boost, -30 dB minimum
    db_volume2 = (volume2 - 100) / 10

    # Apply volume adjustments
    track1 = track1 + db_volume1  # Adjust volume in dB
    track2 = track2 + db_volume2  # Adjust volume in dB

    # Apply EQ and filters to both tracks
    track1 = enhance_audio(track1, eq_type)
    track2 = enhance_audio(track2, eq_type)

    # Apply custom filters
    track1 = apply_filters(track1, high_pass, low_pass)
    track2 = apply_filters(track2, high_pass, low_pass)

    # Crossfade the tracks
    combined = track1.append(track2, crossfade=crossfade_duration)

    # Export the mixed audio to a temporary file
    mixed_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    combined.export(mixed_file_path.name, format="mp3")

    return mixed_file_path.name

# Streamlit app setup
st.title("AI-Powered DJ App (Pro Edition)")
st.write("Upload two audio files and simulate a pro DJ experience!")

# Upload two audio files
uploaded_file1 = st.file_uploader("Choose the first audio file", type=["mp3", "wav"])
uploaded_file2 = st.file_uploader("Choose the second audio file", type=["mp3", "wav"])

# Input for crossfade duration (in milliseconds)
crossfade_duration = st.slider("Crossfade Duration (ms)", min_value=0, max_value=10000, value=3000)

# Input for EQ type
eq_type = st.selectbox("EQ Type", ['None', 'Dance/Electronic', 'Classical', 'Pop'])

# Cue points for both tracks
cue_point1 = st.slider("Cue Point for First Track (ms)", min_value=0, max_value=50000, step=1000, value=0)
cue_point2 = st.slider("Cue Point for Second Track (ms)", min_value=0, max_value=50000, step=1000, value=0)

# Volume sliders for both tracks (0 to 200)
volume1 = st.slider("Volume for First Track (%)", min_value=0, max_value=200, value=100)
volume2 = st.slider("Volume for Second Track (%)", min_value=0, max_value=200, value=100)

# High-pass and low-pass filter settings
high_pass = st.slider("High-pass Filter (Hz)", min_value=0, max_value=10000, value=0)
low_pass = st.slider("Low-pass Filter (Hz)", min_value=0, max_value=10000, value=10000)


# Button to start mixing
if st.button('Start Mixing'):
    if uploaded_file1 and uploaded_file2:
        with st.spinner('Mixing audio like a pro...'):
            mixed_file_path = process_audio(uploaded_file1, uploaded_file2, crossfade_duration, eq_type, cue_point1, cue_point2, volume1, volume2, high_pass, low_pass)
            st.success("Files mixed successfully!")
            st.audio(mixed_file_path)  # Play the mixed audio

            # Download button
            with open(mixed_file_path, 'rb') as f:
                st.download_button(label="Download Mixed Audio", data=f, file_name="mixed_track.mp3", mime="audio/mp3")
    else:
        st.error("Please upload both audio files.")

st.write('Need a spotify to mp3 conerter? Convert here: https://spotmate.online/')
