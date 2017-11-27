package teaType._debug.commonTests;

import java.awt.Color;

import javax.swing.JFrame;

public class GraphicsTest {
	
	public static void main(String[] args) {
		JFrame frame = new JFrame();
		
		firstGraphics fG = new firstGraphics(50, 50, 150, Color.BLACK);
		
		frame.add(fG);
        frame.setSize(750, 600);
        frame.setVisible(true);
                
        while(true){
        	fG.orbit();
        }
	}
}
