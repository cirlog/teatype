package teaType._libraryTest;

import teaType.util.io.Time;

public class Time_Test {
	public static void main(String[] args) throws InterruptedException {
		Time t = new Time();
		
		t.start();
		Thread.sleep((int) (Math.random()*10000));
		t.stop();
		t.print(true, true, true);
	}
}