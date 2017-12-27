package teaType.util.rigid;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class Writer {
	private static FileWriter fw;

	public static void stringToFile(String content, File file, boolean append) {
		try {
			fw = new FileWriter(file, append);
			fw.write(content);
			fw.close();
		} catch (IOException e) {			
			e.printStackTrace();
		}
	}

	public static void stringArrayToFile(String[] arr, File file, boolean create, boolean append, boolean whitespace) {
		try {
			if(create) {
				file.delete();
				file.createNewFile();
			}
			fw = new FileWriter(file, append);
			for(int i = 0; i < arr.length; i++) {
				fw.write(arr[i]);
				if(whitespace) {
					fw.write("\n");
				}
			}
			fw.close();
		} catch (IOException e) {			
			e.printStackTrace();
		}
	}
}
