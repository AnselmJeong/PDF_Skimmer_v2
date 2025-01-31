import gradio as gr
from config import CONFIG
from skimmer import PDFSkimmer

BASE_DIR = CONFIG["directories"]["base_dir"]
gr.set_static_paths(paths=[BASE_DIR])


def create_interface():
    skimmer = PDFSkimmer()

    with gr.Blocks(css="body { width: 100vw; }") as demo:
        with gr.Row():
            with gr.Column(scale=1):
                # Left side - File selection
                gr.Markdown("# PDF Skimmer")
                file_explorer = gr.FileExplorer(
                    root_dir=BASE_DIR,
                    glob="**/*.pdf",
                    file_count="single",
                    label="Select PDF",
                )
            with gr.Column(scale=2):
                gr.Markdown("### Paper Summary")

                with gr.Tabs():
                    tab_names = CONFIG["display"]["tab_names"]
                    tab_icons = CONFIG["display"]["tab_icons"]
                    textboxes = []

                    for name, icon in zip(tab_names, tab_icons):
                        with gr.Tab(f"{icon} {name}"):
                            textboxes.append(gr.Textbox(label=name, lines=10))

        def select_pdf(file_path: str):
            if not file_path:
                return [None] * 6  # Return None for all 6 textboxes

            result = skimmer.load_or_summary(file_path)
            if result is None:
                return [None] * 6

            # Extract values from dictionary in the order matching our components
            return (
                result["core_question"],  # For core_question textbox
                result["introduction"],  # For introduction textbox
                result["methodology"],  # For methodology textbox
                result["results"],  # For results textbox
                result["discussion"],  # For discussion textbox
                result["limitations"],  # For limitations textbox
            )

        file_explorer.change(select_pdf, inputs=[file_explorer], outputs=textboxes)

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
