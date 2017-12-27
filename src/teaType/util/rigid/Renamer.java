package teaType.util.rigid;

import java.io.File;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Renamer {
	public static void main(String[] args) {
		String dir = "/Users/burak/downloads/";

		String name = "K";
		Pattern p = Pattern.compile("^[" + name + name.toLowerCase() + "]+?.*");

		String filename = "KD - Demon Souls";
		String extension = "mp4";

		massRename(dir, p, filename, extension, true);
	}

	public static void massRename(String dir, Pattern name, String filename, String extension, boolean withZero) {
		Matcher m;

		int count = 1;

		File tempDir = new File(dir);
		File[] files = tempDir.listFiles();
		File r;
		for(File f : files) {
			if(f.isDirectory()) {
				continue;
			} else {
				m = name.matcher(f.getName());
				if(m.find()) {
					if(withZero) {
						r = new File(dir + filename + " 0" + count + "." + extension);
						if(count >= 10) {
							r = new File(dir + filename + " " + count + "." + extension);
						}
					} else {
						r = new File(dir + filename + " " + count + "." + extension);
					}
					count++;
					f.renameTo(r);
				} else {
					continue;
				}
			}
		}
	}
}