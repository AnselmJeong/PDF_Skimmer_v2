import gradio as gr
from pathlib import Path
from db_manager import DatabaseManager
from config import CONFIG
from skimmer import PDFSkimmer
import os
from utils import paragraph_to_markdown_list
from chatbot import Chatbot

BASE_DIR = CONFIG["directories"]["base_dir"]

db_manager = DatabaseManager()
skimmer = PDFSkimmer()
dialogue_bot = Chatbot(type="chatbot")

with gr.Blocks(
    css="""
    #file_explorer {
        font-size: 12px;
    }
    #file_explorer * {
        font-size: 12px !important;
    }
    #file_explorer .file-explorer-files {
        font-size: 12px !important;
    }
    #file_explorer .file-explorer-files span {
        font-size: 12px !important;
    
    .gradio-container {
        height: 100vh !important;
    }
    .gradio-column {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    #chatbox {
        flex-grow: 1;
        height: 100% !important;
    }
    .gradio-container-5-14-0 .prose {
        font-size: larger !important;
    }
    """,
    fill_height=True,
    fill_width=True,
) as demo:
    with gr.Sidebar():
        gr.Markdown("# � PDF Skimmer")

        provider_selector = gr.Dropdown(
            choices=["gemini", "openai", "deepseek", "qwen"], label="Model Provider", value="gemini"
        )

        def change_provider(provider: str):
            global skimmer
            skimmer = PDFSkimmer(provider=provider)
            global dialogue_bot
            dialogue_bot = Chatbot(type="chatbot", provider=provider)

        provider_selector.change(fn=change_provider, inputs=[provider_selector])

    with gr.Row():
        with gr.Column():
            file_explorer = gr.FileExplorer(
                root_dir=BASE_DIR,
                file_count="single",
                glob="**/*.pdf",
                label="PDF Files",
                elem_id="file_explorer",
                min_height="95vh",
            )
        with gr.Column():
            gr.Markdown("## Paper Summary")

            with gr.Tabs():
                tab_names = CONFIG["display"]["tab_names"]
                tab_icons = CONFIG["display"]["tab_icons"]
                textboxes = []

                for ix, (name, icon) in enumerate(zip(tab_names, tab_icons)):
                    with gr.Tab(f"{icon} {name}"):
                        # textboxes.append(gr.Textbox(label=name, lines=12, scale=1))
                        textboxes.append(gr.Markdown(label=name, elem_id=f"box{ix}"))

            summarize_again_btn = gr.Button("Summarize Again")

            gr.Markdown("## Chat with the paper")
            chatbox = gr.Chatbot(
                type="messages",
                label="Langchain Agent",
                min_height="45vh",
                elem_id="chatbox",
            )
            with gr.Group():
                with gr.Row():
                    input = gr.Textbox(lines=1, scale=10, show_label=False, container=False)
                    save_button = gr.Button("Save", scale=1)

            def select_pdf(file_path: str):
                if not file_path:
                    return [None] * 6  # Return None for all 6 textboxes

                result = skimmer.load_or_summary(file_path)
                if result is None:
                    return [None] * 6

                # Extract values from dictionary in the order matching our components
                return (
                    paragraph_to_markdown_list(result["core_question"]),
                    paragraph_to_markdown_list(result["introduction"]),
                    paragraph_to_markdown_list(result["methodology"]),
                    paragraph_to_markdown_list(result["results"]),
                    paragraph_to_markdown_list(result["discussion"]),
                    paragraph_to_markdown_list(result["limitations"]),
                )

            def load_chat_history(file_path):
                if not file_path or not isinstance(file_path, (str, os.PathLike)):
                    return []
                try:
                    file_name = Path(file_path).name
                    chat_record = db_manager.get_chat_history(file_name)
                    if chat_record:
                        return chat_record
                    return []
                except Exception as e:
                    print(f"Error loading chat history: {str(e)}")
                    return []

            # Add file_explorer change event to load chat history

            def save_chat_history(file_path: str, history: list):
                if not file_path:
                    return gr.Error("Please select a file first")
                try:
                    file_name = Path(file_path).name
                    db_manager.save_chat_history(file_name, history)
                    gr.Info("Chat history saved successfully")
                except Exception as e:
                    gr.Error(f"Error saving chat history: {str(e)}")

            def _handle_chat(input: str, history: list):
                history.append({"role": "user", "content": input})

                response = dialogue_bot.query_llm(input, history)

                # response = f"This is a {len(history)} test response"
                history.append({"role": "assistant", "content": response})
                return "", history

            save_button.click(fn=save_chat_history, inputs=[file_explorer, chatbox])

            input.submit(_handle_chat, [input, chatbox], [input, chatbox])
            file_explorer.change(fn=select_pdf, inputs=[file_explorer], outputs=textboxes).then(
                fn=load_chat_history, inputs=[file_explorer], outputs=[chatbox]
            )
            # file_explorer.change(fn=get_summary, inputs=file_explorer, outputs=[result])

            def force_summarize(file_path: str):
                if not file_path:
                    return [None] * 6

                result = skimmer.force_summary(file_path)
                if result is None:
                    return [None] * 6

                return (
                    result["core_question"],
                    result["introduction"],
                    result["methodology"],
                    result["results"],
                    result["discussion"],
                    result["limitations"],
                )

            # Add the click event for summarize_again button
            summarize_again_btn.click(fn=force_summarize, inputs=[file_explorer], outputs=textboxes)

demo.launch()
