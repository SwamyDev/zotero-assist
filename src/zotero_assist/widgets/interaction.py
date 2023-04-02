import json
import streamlit as st

from typing import Sequence, Dict

from pathlib import Path

from streamlit_chat import message

from zotero_assist.constants import get_llaman_index_dir_for_pdf
from zotero_assist.knowledge.retrieve_llama_index_for_pdf import retrieve_llama_index_for_pdf


def load_history_for_pdf(pdf_file: Path) -> Sequence[Dict]:
    history_file = get_llaman_index_dir_for_pdf(pdf_file) / "history.json"
    if history_file.exists():
        return json.loads(history_file.read_text())
    else:
        return []


def save_history_for_pdf(history: Sequence[Dict], pdf_file: Path):
    return (get_llaman_index_dir_for_pdf(pdf_file) / "history.json").write_text(json.dumps(history))


class RemoveQuery:
    def __init__(self):
        self.response = "42"
        self.extra_info = dict(source_pdf="/home/some/pdf.pdf", page_idx=3)

    def get_formatted_sources(self):
        return "the formatted sources"


class Interaction:
    def __init__(self, session):
        self.session = session

    def load_selected_history(self, history_container) -> None:
        pdf_file = self.session['selected_pdf']
        self.session['chat_history'] = load_history_for_pdf(pdf_file)
        max_history = min(self.session['max_history'], len(self.session['chat_history']))
        with history_container:
            st.write("""<div class='YScrollMarker'/>""", unsafe_allow_html=True)
            for i, msg in enumerate(self.session['chat_history'][-max_history:]):
                message(msg['content'], is_user=msg['user'], key=str(i))

    def send_to_selected(self, msg: str, history_container, mode=None):
        pdf_file = self.session['selected_pdf']
        interaction_index = retrieve_llama_index_for_pdf(pdf_file)
        # query = interaction_index.query(msg, mode=mode or 'default')
        query = RemoveQuery()
        self.session['query'] = dict(page_idx=query.extra_info['page_idx'], source=query.get_formatted_sources())
        response = query.response
        history = self.session['chat_history']
        i = len(history)
        history.append({'content': msg, 'user': True})
        history.append({'content': response, 'user': False})
        save_history_for_pdf(history, pdf_file)
        with history_container:
            message(msg, is_user=True, key=str(i))
            message(response, is_user=False, key=str(i + 1))
