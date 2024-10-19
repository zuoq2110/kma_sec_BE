import subprocess
import tempfile
from importlib.metadata import metadata
from os import environ
from subprocess import Popen, PIPE
from typing import Annotated, Optional

import joblib
from bson import ObjectId
from fastapi import Depends, UploadFile
from markdown_it.common.html_re import attribute
from pyexpat import features

from src.data.local import PdfApplicationLocalDataSource
from .model import ModelRepository
from ..local.document import as_pdf_application_details
from ..local.document.pdf_application import as_pdf_application
from ...domain.data.model import PdfApplication

# Configure the Tensorflow logging module
environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


class PdfApplicationRepository:

    def __init__(
            self,
            local_data_source: Annotated[PdfApplicationLocalDataSource, Depends()],
            model_repository: Annotated[ModelRepository, Depends()]
    ):
        self.__local_data_source = local_data_source
        self.__model_repository = model_repository

    async def merge_dicts(self, dict_array, field_name):
        merged = {}
        if isinstance(dict_array, dict):
            # Nếu dict_array là một dict đơn lẻ, chỉ cần trả về nó
            return {field_name: dict_array}
        for d in dict_array:
            if isinstance(d, dict):
                merged.update(d)
            else:
                print(f"Skipping non-dict item: {d}")
        return {field_name: merged}

    async def create_application_analysis(self, file: UploadFile, token: Optional[str]) -> dict:
        print("file2", file)
        malware_type, metadata = await self.__get_application_malware_type(file=file)

        print("metadata:", metadata)
        merged_metadata = await self.merge_dicts(metadata, "attributes")
        print("merged_metadata:", merged_metadata)
        merged_metadata["name"] = file.filename

        print("malware_type:", malware_type)

        try:
            document_id = await self.__local_data_source.insert(metadata=merged_metadata, malware_type=malware_type,
                                                                token=token if token else None)
        except Exception as e:
            # Handle the exception here, e.g., log an error or raise a custom exception
            print(f"Error during insertion: {e}")
            raise Exception("Failed to insert document")
        print("document_id:",document_id)
        return str(object=document_id)

    async def get_analyses(self, page: int = 1, limit: int = 20) -> list:
        cursor = await self.__local_data_source.find_all(page=page, limit=limit)
        analyses = [as_pdf_application(document=document) for document in cursor]
        print(analyses)
        return analyses

    async def get_analysis_details(self, analysis_id: str) -> Optional[PdfApplication]:
        id = ObjectId(oid=analysis_id)
        document = await self.__local_data_source.find_by_id(document_id=id)

        return None if document is None else as_pdf_application_details(document=document)


    async def __get_application_malware_type(self, file: UploadFile) :
        print("ádads")
        attribute={}
        clf_loaded = joblib.load('./.docker/data/files/models/random_forest_model.pkl')
        print(clf_loaded)

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.file.read())
            temp_filename = tmp_file.name


        features, attribute1 = await self.feature_extraction(temp_filename)
        attribute.update(attribute1)

        result = clf_loaded.predict(features)
        print('Result:', result[0])
        if result[0].lower() == 'no':
            mapped_result = 'Benign'
        elif result[0].lower() == 'yes':
            mapped_result = 'Malware'
        return mapped_result, attribute

    async def get_attribute(self,file: UploadFile) -> dict:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.file.read())
            temp_filename = tmp_file.name
        features, attribute = await self.feature_extraction(temp_filename)
        print(attribute)

        return attribute

    async def feature_extraction(self,filepath):
        features = []
        attribute = {}
        command_to_execute = 'python "src\\data\\repository\\pdfid.py" "' + filepath + '"'

        stdout = Popen(command_to_execute, shell=True, stdout=PIPE).stdout
        print(stdout)
        output = stdout.readlines()
        print(output)
        print(len(output))

        if len(output) == 24:
            features1, attribute1 =await self.extract_featues(output)
            features.append(features1)
            attribute.update(attribute1)


        print("features:",features)
        print("attribute:",attribute)

        return features, attribute




    async def extract_featues(self, output):
        tuples = []
        attribute = {}
        obj_subsection = bytes(output[2])
        obj_subsection = obj_subsection.replace(b'obj', b'')
        obj_subsection = obj_subsection.replace(b' ', b'')
        obj_subsection = obj_subsection.replace(b'\\n', b'')
        obj_subsection = obj_subsection.decode('UTF-8')
        try:
            obj = int(obj_subsection)
            attribute["obj"] = obj
            tuples.append(obj)
        except ValueError:
            obj = 10
            tuples.append(obj)
            pass

        endobj_subsection = bytes(output[3])
        endobj_subsection = endobj_subsection.replace(b'endobj', b'')
        endobj_subsection = endobj_subsection.replace(b' ', b'')
        endobj_subsection = endobj_subsection.replace(b'\\n', b'')
        endobj_subsection = endobj_subsection.decode('UTF-8')
        try:
            obj = int(endobj_subsection)
            attribute["endobj"] = obj

            tuples.append(obj)
        except ValueError:
            obj = 10
            tuples.append(obj)
            pass

        stream_subsection = bytes(output[4])
        stream_subsection = stream_subsection.replace(b'stream', b'')
        stream_subsection = stream_subsection.replace(b' ', b'')
        stream_subsection = stream_subsection.replace(b'\\n', b'')
        stream_subsection = stream_subsection.decode('UTF-8')
        try:
            stream = int(stream_subsection)
            attribute["stream"] = stream

            tuples.append(stream)
        except ValueError:
            stream = 3
            tuples.append(stream)
            pass

        endstream_subsection = bytes(output[5])
        endstream_subsection = endstream_subsection.replace(b'endstream', b'')
        endstream_subsection = endstream_subsection.replace(b' ', b'')
        endstream_subsection = endstream_subsection.replace(b'\\n', b'')
        endstream_subsection = endstream_subsection.decode('UTF-8')
        try:
            endstream = int(endstream_subsection)
            attribute["endstream"] = endstream

            tuples.append(endstream)
        except ValueError:
            endstream = 3
            tuples.append(endstream)
            pass

        xref_subsection = bytes(output[6])
        xref_subsection = xref_subsection.replace(b'xref', b'')
        xref_subsection = xref_subsection.replace(b' ', b'')
        xref_subsection = xref_subsection.replace(b'\\n', b'')
        xref_subsection = xref_subsection.decode('UTF-8')
        try:
            xref = int(xref_subsection)
            attribute["xref"] = xref

            tuples.append(xref)
        except ValueError:
            xref = 1
            tuples.append(xref)
            pass

        trailer_subsection = bytes(output[7])
        trailer_subsection = trailer_subsection.replace(b'trailer', b'')
        trailer_subsection = trailer_subsection.replace(b' ', b'')
        trailer_subsection = trailer_subsection.replace(b'\\n', b'')
        trailer_subsection = trailer_subsection.decode('UTF-8')
        try:
            trailer = int(trailer_subsection)
            attribute["trailer"] = trailer

            tuples.append(trailer)
        except ValueError:
            trailer = 1
            tuples.append(trailer)
            pass

        startxref_subsection = bytes(output[8])
        startxref_subsection = startxref_subsection.replace(b'startxref', b'')
        startxref_subsection = startxref_subsection.replace(b' ', b'')
        startxref_subsection = startxref_subsection.replace(b'\\n', b'')
        startxref_subsection = startxref_subsection.decode('UTF-8')
        try:
            startxref = int(startxref_subsection)
            attribute["startxref"] = startxref

            tuples.append(startxref)
        except ValueError:
            startxref = 1
            tuples.append(startxref)
            pass

        Page_subsection = bytes(output[9])
        Page_subsection = Page_subsection.replace(b'/Page', b'')
        Page_subsection = Page_subsection.replace(b' ', b'')
        Page_subsection = Page_subsection.replace(b'\\n', b'')
        Page_subsection = Page_subsection.decode('UTF-8')
        try:
            Page = int(Page_subsection)
            attribute["Page"] = Page

            tuples.append(Page)
        except ValueError:
            Page = 1
            tuples.append(Page)
            pass

        Encrypt_subsection = bytes(output[10])
        Encrypt_subsection = Encrypt_subsection.replace(b'/Encrypt', b'')
        Encrypt_subsection = Encrypt_subsection.replace(b' ', b'')
        Encrypt_subsection = Encrypt_subsection.replace(b'\\n', b'')
        Encrypt_subsection = Encrypt_subsection.decode('UTF-8')
        try:
            Encrypt = int(Encrypt_subsection)
            attribute["Encrypt"] = Encrypt

            tuples.append(Encrypt)
        except ValueError:
            Encrypt = 0
            tuples.append(Encrypt)
            pass

        ObjStm_subsection = bytes(output[11])
        ObjStm_subsection = ObjStm_subsection.replace(b'/ObjStm', b'')
        ObjStm_subsection = ObjStm_subsection.replace(b' ', b'')
        ObjStm_subsection = ObjStm_subsection.replace(b'\\n', b'')
        ObjStm_subsection = ObjStm_subsection.decode('UTF-8')
        try:
            ObjStm = int(ObjStm_subsection)
            attribute["ObjStm"] = ObjStm

            tuples.append(ObjStm)
        except ValueError:
            ObjStm = 0
            tuples.append(ObjStm)
            pass

        JS_subsection = bytes(output[12])
        JS_subsection = JS_subsection.replace(b'/JS', b'')
        JS_subsection = JS_subsection.replace(b' ', b'')
        JS_subsection = JS_subsection.replace(b'\\n', b'')
        JS_subsection = JS_subsection.decode('UTF-8')
        try:
            JS = int(JS_subsection)
            attribute["JS"] = JS

            tuples.append(JS)
        except ValueError:
            JS = 1
            tuples.append(JS)
            pass

        JavaScript_subsection = bytes(output[13])
        JavaScript_subsection = JavaScript_subsection.replace(b'/JavaScript', b'')
        JavaScript_subsection = JavaScript_subsection.replace(b' ', b'')
        JavaScript_subsection = JavaScript_subsection.replace(b'\\n', b'')
        JavaScript_subsection = JavaScript_subsection.decode('UTF-8')
        try:
            JavaScript = int(JavaScript_subsection)
            attribute["JavaScript"] = JavaScript

            tuples.append(JavaScript)
        except ValueError:
            JavaScript = 1
            tuples.append(JavaScript)
            pass

        AA_subsection = bytes(output[14])
        AA_subsection = AA_subsection.replace(b'/AA', b'')
        AA_subsection = AA_subsection.replace(b' ', b'')
        AA_subsection = AA_subsection.replace(b'\\n', b'')
        AA_subsection = AA_subsection.decode('UTF-8')
        try:
            AA = int(AA_subsection)
            attribute["AA"] = AA

            tuples.append(AA)
        except ValueError:
            AA = 0
            tuples.append(AA)
            pass

        OpenAction_subsection = bytes(output[15])
        OpenAction_subsection = OpenAction_subsection.replace(b'/OpenAction', b'')
        OpenAction_subsection = OpenAction_subsection.replace(b' ', b'')
        OpenAction_subsection = OpenAction_subsection.replace(b'\\n', b'')
        OpenAction_subsection = OpenAction_subsection.decode('UTF-8')
        try:
            OpenAction = int(OpenAction_subsection)
            attribute["OpenAction"] = OpenAction

            tuples.append(OpenAction)
        except ValueError:
            OpenAction = 1
            tuples.append(OpenAction)
            pass

        AcroForm_subsection = bytes(output[16])
        AcroForm_subsection = AcroForm_subsection.replace(b'/AcroForm', b'')
        AcroForm_subsection = AcroForm_subsection.replace(b' ', b'')
        AcroForm_subsection = AcroForm_subsection.replace(b'\\n', b'')
        AcroForm_subsection = AcroForm_subsection.decode('UTF-8')
        try:
            AcroForm = int(AcroForm_subsection)
            attribute["AcroForm"] = AcroForm

            tuples.append(AcroForm)
        except ValueError:
            AcroForm = 0
            tuples.append(AcroForm)
            pass

        JBIG2Decode_subsection = bytes(output[17])
        JBIG2Decode_subsection = JBIG2Decode_subsection.replace(b'/JBIG2Decode', b'')
        JBIG2Decode_subsection = JBIG2Decode_subsection.replace(b' ', b'')
        JBIG2Decode_subsection = JBIG2Decode_subsection.replace(b'\\n', b'')
        JBIG2Decode_subsection = JBIG2Decode_subsection.decode('UTF-8')
        try:
            JBIG2Decode = int(JBIG2Decode_subsection)
            attribute["JBIG2Decode"] = JBIG2Decode

            tuples.append(JBIG2Decode)
        except ValueError:
            JBIG2Decode = 0
            tuples.append(JBIG2Decode)
            pass

        RichMedia_subsection = bytes(output[18])
        RichMedia_subsection = RichMedia_subsection.replace(b'/RichMedia', b'')
        RichMedia_subsection = RichMedia_subsection.replace(b' ', b'')
        RichMedia_subsection = RichMedia_subsection.replace(b'\\n', b'')
        RichMedia_subsection = RichMedia_subsection.decode('UTF-8')
        try:
            RichMedia = int(RichMedia_subsection)
            attribute["RichMedia"] = RichMedia

            tuples.append(RichMedia)
        except ValueError:
            RichMedia = 0
            tuples.append(RichMedia)
            pass

        Launch_subsection = bytes(output[19])
        Launch_subsection = Launch_subsection.replace(b'/Launch', b'')
        Launch_subsection = Launch_subsection.replace(b' ', b'')
        Launch_subsection = Launch_subsection.replace(b'\\n', b'')
        Launch_subsection = Launch_subsection.decode('UTF-8')
        try:
            Launch = int(Launch_subsection)
            attribute["Launch"] = Launch

            tuples.append(Launch)
        except ValueError:
            Launch = 0
            tuples.append(Launch)
            pass

        EmbeddedFile_subsection = bytes(output[20])
        EmbeddedFile_subsection = EmbeddedFile_subsection.replace(b'/EmbeddedFile', b'')
        EmbeddedFile_subsection = EmbeddedFile_subsection.replace(b' ', b'')
        EmbeddedFile_subsection = EmbeddedFile_subsection.replace(b'\\n', b'')
        EmbeddedFile_subsection = EmbeddedFile_subsection.decode('UTF-8')
        try:
            EmbeddedFile = int(EmbeddedFile_subsection)
            attribute["EmbeddedFile"] = EmbeddedFile

            tuples.append(EmbeddedFile)
        except ValueError:
            EmbeddedFile = 0
            tuples.append(EmbeddedFile)
            pass

        XFA_subsection = bytes(output[21])
        XFA_subsection = XFA_subsection.replace(b'/XFA', b'')
        XFA_subsection = XFA_subsection.replace(b' ', b'')
        XFA_subsection = XFA_subsection.replace(b'\\n', b'')
        XFA_subsection = XFA_subsection.decode('UTF-8')
        try:
            XFA = int(XFA_subsection)
            attribute["XFA"] = XFA

            tuples.append(XFA)
        except ValueError:
            XFA = 0
            tuples.append(XFA)
            pass

        colors_subsection = bytes(output[22])
        colors_subsection = colors_subsection.replace(b'/Colors > 2^24', b'')
        colors_subsection = colors_subsection.replace(b' ', b'')
        colors_subsection = colors_subsection.replace(b'\\n', b'')
        colors_subsection = colors_subsection.decode('UTF-8')
        try:
            colors = int(colors_subsection)
            attribute["colors"] = colors

            tuples.append(colors)
        except ValueError:
            colors = 0
            tuples.append(colors)
            pass
        print(attribute)
        return tuples, attribute
