package teaType.util.io;

import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Clip;

public class SoundFX {
	public void soundFX(String path) {
		try {
			AudioInputStream inputStream = AudioSystem.getAudioInputStream(getClass().getResource(path));
			Clip clip = AudioSystem.getClip();
			clip.open(inputStream);
			clip.start();
		} catch (Exception e) {
			e.printStackTrace();
		}		
	}
}
