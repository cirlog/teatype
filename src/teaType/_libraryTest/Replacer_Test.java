package teaType._libraryTest;

import java.io.File;
import java.io.IOException;

import teaType.util.rigid.Replacer;

public class Replacer_Test {
	public static void main(String[] args) throws IOException {
		File f = new File("./#!m_names.txt");
		Replacer.replaceWithStrings(f);
	}
}