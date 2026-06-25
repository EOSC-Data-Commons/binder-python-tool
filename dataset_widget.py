import ipyparams
import ipywidgets as widgets
from IPython.display import display
import subprocess
import threading
import os
from pathlib import Path


def print_tree(path: Path, prefix: str = ""):
    entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry.name)
        
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(entry, prefix + extension)


def create_widget():
    out = widgets.Output()
    box = widgets.VBox([widgets.Label(value="⏳ Waiting for params...")])
    display(box, out)

    def setup_widget():
        import time
        dataset_url = None
        for _ in range(50):  # 10s timeout
            dataset_url = ipyparams.params.get('dataset_url')
            if dataset_url:
                break
            time.sleep(0.2)

        if not dataset_url:
            box.children = [widgets.Label(value="⚠ No dataset_url param found")]
            return

        label = widgets.Label(value=f"URL: {dataset_url}")
        download_btn = widgets.Button(description="Download Dataset", button_style='primary', icon='download')
        tree_btn = widgets.Button(description="Show Files", button_style='info', icon='folder')

        def on_download_click(b):
            download_btn.disabled = True
            download_btn.description = "Downloading..."
            with out:
                out.clear_output()
                os.makedirs('data', exist_ok=True)
                print(f"Running: datahugger download {dataset_url} --to data/")
                try:
                    result = subprocess.run(
                        ["datahugger", "download", dataset_url, "--to", "data/"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("✓ Done")
                        print(result.stdout)
                    else:
                        print("✗ Failed")
                        print(result.stderr)
                except FileNotFoundError:
                    print("✗ datahugger not found — is it installed?")
                finally:
                    download_btn.disabled = False
                    download_btn.description = "Download Dataset"

        def on_tree_click(b):
            with out:
                out.clear_output()
                path = Path("data")
                if not path.exists():
                    print("⚠ 'data/' folder does not exist")
                    return
                
                print(path.name)
                print_tree(path)

        download_btn.on_click(on_download_click)
        tree_btn.on_click(on_tree_click)

        box.children = [label, widgets.HBox([download_btn, tree_btn])]

    threading.Thread(target=setup_widget, daemon=True).start()
