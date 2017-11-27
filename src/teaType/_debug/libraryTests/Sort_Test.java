package teaType._debug.libraryTests;

import teaType.util.Array
;
import teaType.util.statics.Print;
import teaType.util.statics.Randomizer;

public class Sort_Test {
	public static void main(String[] args) {
		int[] arr = Randomizer.generateInteger(20, 1000, false, false, false);
		Array.quicksort(arr, true);
		Print.integerArray(arr, true, true);
	}
}