import java.io.*;
import java.util.Scanner;

class RunPython {
    public static void main(String[] args) throws IOException {
        Process process =
                new ProcessBuilder("python", "human_sim.py")
                        .redirectErrorStream(true)
                        .start();

        Scanner scan = new Scanner(System.in);

        BufferedReader pythonOutput = new BufferedReader(new InputStreamReader(process.getInputStream()));
        BufferedWriter pythonInput = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));

        Thread thread = new Thread(() -> {
            String input;
            while (process.isAlive() && (input = scan.nextLine()) != null) {
                try {
                    pythonInput.write(input);
                    pythonInput.newLine();
                    pythonInput.flush();
                } catch (IOException e) {
                    System.out.println(e.getLocalizedMessage());
                    process.destroy();
                    System.out.println("Python program terminated.");
                }
            }
        });
        thread.start();

        String output;
        while (process.isAlive() && (output = pythonOutput.readLine()) != null) {
            System.out.println(output);
        }
        pythonOutput.close();
        pythonInput.close();
    }
}