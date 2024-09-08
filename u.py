import telebot 
from telebot import types
import whisper
import pdfkit
import jinja2
from langchain.chains import LLMChain
from langchain_community.llms import YandexGPT
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from html2docx import html2docx 


def convert_html_to_pdf(
    html_string,
    template_folder: str = "html",
    base_html_file: str = "base.html",
    output_file: str = "generate_pdf.pdf",
    output_folder: str = "pdf",) -> str:
        if output_folder.endswith("/"):
            raise ValueError("Wrong output folder name, should not end with '/'")
        else:
            pdf_file_name = f"{output_folder}/{output_file}"

        try:
            template_loader = jinja2.FileSystemLoader(template_folder)
            print(template_loader)
            template_env = jinja2.Environment(loader=template_loader)
            print(template_env)
            basic_template = template_env.get_template(base_html_file)
            print(basic_template)
            output_html_code = basic_template.render()
            print(output_html_code)
            # print(output_html_code)
           
           

            # render content, this if for once we have AI generated response
            
            output_html_code = basic_template.render(
                segments=html_string
            )


            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-bottom': '0.75in',
                'margin-right': '0.55in',
                'margin-left': '0.55in',
                'encoding': "UTF-8",
                'footer-right': '[page] of [topage]',
                'footer-font-size': "9",
                'custom-header': [
                    ('Accept-Encoding', 'gzip')
                ],
                'enable-local-file-access': True,
                'no-outline': None,
                'enable-local-file-access': True,
                'no-outline': None
            }

            pdfkit.from_string(
                input=output_html_code,
                output_path=pdf_file_name,
                options=options
            )

            buf = html2docx(output_html_code, title="Расшифровка")
            with open(f"{output_file[:-3]}docx", "wb") as fp:
                fp.write(buf.getvalue())
        except Exception as e:
            # good to log this exception instead
            print(e)
            return ""

        return pdf_file_name