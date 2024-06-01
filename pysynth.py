import os
import threading
import tkinter as tk
from tkinter import filedialog
import subprocess
import psutil

class FluidSynthPlayer:
    def __init__(self, master):
        self.master = master
        self.process = None
        self.playing = False

        master.title("FluidSynth MIDI Player")
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sf2_label = tk.Label(master, text="SF2 Soundfont File:")
        self.sf2_label.pack()
        self.sf2_entry = tk.Entry(master, width=50)
        self.sf2_entry.pack()
        self.sf2_browse = tk.Button(master, text="Browse", command=self.browse_sf2)
        self.sf2_browse.pack()

        self.midi_label = tk.Label(master, text="MIDI File:")
        self.midi_label.pack()
        self.midi_entry = tk.Entry(master, width=50)
        self.midi_entry.pack()
        self.midi_browse = tk.Button(master, text="Browse", command=self.browse_midi)
        self.midi_browse.pack()

        self.play_button = tk.Button(master, text="Play MIDI", command=self.play_midi)
        self.play_button.pack()

        self.stop_button = tk.Button(master, text="Stop MIDI", command=self.stop_midi, state=tk.DISABLED)
        self.stop_button.pack()

        self.result_label = tk.Label(master, text="")
        self.result_label.pack()

    def browse_sf2(self):
        sf2_file = filedialog.askopenfilename(filetypes=[("SF2 files", "*.sf2")])
        if sf2_file:
            self.sf2_entry.delete(0, tk.END)
            self.sf2_entry.insert(0, sf2_file)

    def browse_midi(self):
        midi_file = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid")])
        if midi_file:
            self.midi_entry.delete(0, tk.END)
            self.midi_entry.insert(0, midi_file)

    def play_midi(self):
        sf2_file = self.sf2_entry.get()
        midi_file = self.midi_entry.get()

        if os.path.isfile(sf2_file) and os.path.isfile(midi_file):
            self.result_label.config(text="Playing MIDI...")
            self.play_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.playing = True
            self.thread = threading.Thread(target=self.run_fluidsynth, args=(sf2_file, midi_file))
            self.thread.daemon = True
            self.thread.start()
        else:
            self.result_label.config(text="Please select valid SF2 and MIDI files.")

    def run_fluidsynth(self, sf2_file, midi_file):
        command = ['fluidsynth', '-ni', sf2_file, midi_file]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.process.communicate()
        self.playing = False
        self.master.after(0, self.on_playback_complete)

    def stop_midi(self):
        if self.playing:
            stop_thread = threading.Thread(target=self.terminate_process)
            stop_thread.daemon = True
            stop_thread.start()

    def terminate_process(self):
        if self.process:
            proc = psutil.Process(self.process.pid)
            for child in proc.children(recursive=True):
                child.terminate()
            proc.terminate()
            gone, still_alive = psutil.wait_procs([proc], timeout=3)
            for p in still_alive:
                p.kill()
        self.playing = False
        self.master.after(0, self.on_playback_complete)

    def on_playback_complete(self):
        self.result_label.config(text="Playback finished or stopped.")
        self.play_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def on_close(self):
        if self.playing:
            self.terminate_process()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = FluidSynthPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
