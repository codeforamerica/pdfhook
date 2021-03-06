
import json
from urllib.parse import urlparse
from tests.test_base import BaseTestCase
from tests.mock.factories import PDFFormFactory
from flask import url_for
from src.main import db
from src.pdfhook.serializers import (
    PDFFormIndexDumper, PDFFormDumper
    )


class TestViews(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.pdfs = [PDFFormFactory.create() for i in range(3)]
        db.session.commit()

    def test_index_view_returns_html(self):
        response = self.client.get(
            url_for('pdfhook.index')
            )
        self.assertIn(
            'Upload a PDF Form to Try It Out',
            response.data.decode('utf-8')
        )

    def test_index_get_accept_json_returns_json_index_of_forms(self):
        dumper = PDFFormIndexDumper()
        sorted_pdfs = sorted(self.pdfs,
            key=lambda p: p.latest_post,
            reverse=True)
        serialized_pdfs = dumper.dump(
            sorted_pdfs, many=True).data
        response = self.client.get(
            url_for('pdfhook.index'),
            headers=[('Accept', 'application/json')])
        data = json.loads(response.data.decode('utf-8'))
        expected = dict(pdf_forms=serialized_pdfs)
        self.assertDictEqual(expected, data)

    def test_get_pdf_json_returns_serialized_pdf(self):
        url = url_for('pdfhook.fill_pdf', pdf_id=self.pdfs[0].id)
        response = self.client.get(url, headers=[('Accept', 'application/json')])
        dumper = PDFFormDumper()
        expected = dumper.dump(self.pdfs[0]).data
        data = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual(expected, data)

    def test_delete_pdf_returns_clean_index(self):
        url = url_for('pdfhook.delete_pdf', pdf_id=self.pdfs[0].id)
        pdf_name = self.pdfs[0].original_pdf_title
        response = self.client.post(url, follow_redirects=True)
        response_html = response.data.decode('utf-8')
        self.assertNotIn(pdf_name, response_html)
