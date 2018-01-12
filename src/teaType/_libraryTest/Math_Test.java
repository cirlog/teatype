package teaType._libraryTest;

import java.io.PrintWriter;

public class Math_Test {
	public static void main(String[] args) {
		PrintWriter out = new PrintWriter(System.out, true);

		int retries = 10000;
		int c = 0;
		double sum = 0.0;
		while(c < retries) {
			int count = 0;
			int tries = 10000;
			for(int i = 0; i < tries; i++) {
				double random = Math.random();
				double roll = 20;
				if(random < roll/100) {
					//out.println(Math.random());
					count++;
				}
			}
			sum+= (double) count/tries;
			System.err.println("\n" + count + " out of " + tries + " tries & Percentage: " + (double) count/tries + "%");
			c++;
		}
		sum/= retries;
		out.println("\nFinal percentage: Results/" + retries + " = " + sum + "%");
	}
}