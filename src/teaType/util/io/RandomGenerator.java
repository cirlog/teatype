package teaType.util.io;

import java.util.Random;

public class RandomGenerator {
	protected int wordAmount;
	protected String[] sA;
	protected Random rnd = new Random();

	public RandomGenerator() {
	}

	public String[] generate (int wordAmount, int length, String[] array) {
		sA = new String [wordAmount];
		for (int i = 0; i < wordAmount; i++) {
			StringBuilder sb = new StringBuilder();
			for(int i2 = 0; i2 < length; i2++) {
				String c = array[rnd.nextInt(array.length)];
				sb.append(c);
			}
			sA[i] = sb.toString();
		}
		return sA;
	}

	public String[] randomGenerate (int wordAmount, int length, String[] array) {
		sA = new String [wordAmount];
		for (int i = 0; i < wordAmount; i++) {
			StringBuilder sb = new StringBuilder();
			int r = ((int) (Math.random()*20+3));
			for(int i2 = 0; i2 < r; i2++) {
				String c = array[rnd.nextInt(array.length)];
				sb.append(c);
			}
			sA[i] = sb.toString();
		}
		return sA;
	}
}