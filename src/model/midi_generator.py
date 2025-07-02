from basic_pitch.inference import predict, predict_and_save, Model
from basic_pitch import ICASSP_2022_MODEL_PATH
# Prototype
# predict_and_save(
#     <input-audio-path-list>,
#     <output-directory>,
#     <save-midi>,
#     <sonify-midi>,
#     <save-model-outputs>,
#     <save-notes>,
# )
#model_output, midi_data, note_events = predict("input/audio/file.wav")
class audio_conversion():
    def __init__(self, song:str = 'default_song', 
                 audio_path: str = 'data/raw', 
                 output_path: str = 'output/model_midi'):
        
        self.audio_path = f'{audio_path}/{song}/{song}.mp3'
        self.output_path = output_path
    
    def conversion_1(self):
        print("🔍 Lade Audio:", self.audio_path)
        print("📂 Speichere nach:", self.output_path)

        predict_and_save(audio_path_list=[self.audio_path], output_directory=self.output_path, 
                         save_midi=True, sonify_midi=False, 
                         save_model_outputs=True, save_notes=True,
                         model_or_model_path=ICASSP_2022_MODEL_PATH)

if __name__== '__main__':
    # Example usage
    # audio_conversion(song='OMORI_cleaner', audio_path='data/raw', output_path='output/model_midi')
    # modell = audio_conversion(song='OMORI_cleaner')
    # modell.conversion_1()
    print("This is a prototype for audio conversion to MIDI using Basic Pitch.")



# def convert_audio(song:str, audio_path: str, output_path: str):
#     audio_path = 'data/raw/{song}.mp3'
#     output_path = 'output/model_midi'

    
    
    
#convert_audio('OMORI_Final-Duet')