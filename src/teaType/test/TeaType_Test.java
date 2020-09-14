package teatype.test;

import teatype.datatype.TeaType;
import teatype.io.Random;

public class TeaType_Test {
	public static void main(String[] args) throws Exception {		
		TeaType<Object> tt = new TeaType<Object>();
		int[] arr = Random.generateInteger(25, 10, false, false, false);

		tt.forbidDuplicates();
		tt.allowDuplicates();
		
		for(int i : arr) {
			tt.add(i);
		}
		tt.lock();
		tt.push(1);
		tt.push(10);
		
		tt.print();
	}
}