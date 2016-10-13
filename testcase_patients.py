from test_library import *
from vtest import *
import time
import random

class testcase_patients(VTest):

    def __init__(self):
        self.grid_id = '#grid-patrefrequests'
        self.editor_filename = "./json/patient_editor.json"
        self.detail_view_filename = "../client/app/secure/json/common/patients.json"
        self.patient_editor_fields = json.loads(open(self.editor_filename, 'r').read())
        self.patient_detail_view_fields = json.loads(open(self.detail_view_filename, 'r').read())
        self.detail_view_config = {
            "config_name": "patient_detail_view",
            "label_method": "css",
            "label_selector_pattern": "[data-details=\'{0}-details\']",
            "input_method": "id",
            "input_selector_pattern": "{0}"
        }
        self.editor_config = {
            "config_name": "patient_editor",
            "label_method": "id",
            "label_selector_pattern": "{0}-label",
            "input_method": "id",
            "input_selector_pattern": "selector-idpatient-{0}"
        }
        # When running a test method, the fail flag will be initialized to False, and change to True when a failure assertion is detected.
        self.fail = None
        self.log = []


    @VTest.category('patient')
    @VTest.category('patient_detail_view')
    @VTest.category('patient_list_of_fields')
    def when_selecting_a_PATIENT_DETAIL_VIEW_expect_to_see_a_LIST_OF_FIELDS_correctly(self):
        if lib_go_to_a_patient_detail_view(self):
            lib_check_list_of_fields(self.patient_detail_view_fields, self.detail_view_config, self)

    @VTest.category('patient')
    @VTest.category('patient_editor')
    @VTest.category('patient_list_of_fields')
    def when_selecting_a_PATIENT_EDITOR_expect_to_see_a_LIST_OF_FIELDS_correctly(self):
        # Go to a random patref detail view
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        if patref_id:
            # Click on the Patient field to see the patient editor
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = "[data-details='selector-idpatient-details']"
            self.click_element(**param)

            lib_check_list_of_fields(self.patient_editor_fields, self.editor_config, self)

    @VTest.category('patient')
    @VTest.category('patient_editor')
    @VTest.category('save_option')
    @VTest.category('read_from_editor')
    def when_POPULATING_and_SAVING_PATIENT_EDITOR_expect_to_see_the_save_and_refresh_option_work_well(self):
        '''
        Steps:
        - go to some patient editor,
        - populate new random values,
        - store the new values in a variable,
        - click the save option,
        - compare the stored values with the refreshed values on the screen.
        '''
        # Go to a random patref detail view
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        if patref_id:
            # Click on the Patient field to see the patient editor
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = "[data-details='selector-idpatient-details']"
            self.click_element(**param)
            lib_data_populate(self.patient_editor_fields, self.editor_config, self)
            updated_patient = lib_read_data_from_editor_or_detail_view(self.patient_editor_fields, self.editor_config, self)
            lib_click_save_button(self)
            lib_assert_data(updated_patient, self.patient_editor_fields, self.editor_config, self)

    @VTest.category('patient')
    @VTest.category('patient_editor')
    @VTest.category('save_option')
    @VTest.category('read_from_editor')
    def when_POPULATING_and_SAVING_PATIENT_EDITOR_expect_to_see_the_saved_patient_when_coming_from_the_main_menu(self):
        '''
        Steps:
        - go to some patient editor,
        - populate new random values,
        - click the save option,
        - store the new values in a variable,
        - go to that patient editor again from the main menu,
        - compare the stored values with the values on the screen.
        '''
        # Go to a random patref detail view
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        if patref_id:
            # Click on the Patient field to see the patient editor
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = "[data-details='selector-idpatient-details']"
            self.click_element(**param)
            lib_data_populate(self.patient_editor_fields, self.editor_config, self)
            lib_click_save_button(self)
            updated_patient = lib_read_data_from_editor_or_detail_view(self.patient_editor_fields, self.editor_config, self)

            # Go to that patient editor again from the main menu
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="patRefsMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="allReferrals()"]'
            self.click_element(**param)
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": patref_id, "object_ids": patref_ids})
            # Click on the Patient field to see the patient editor
            param["selector"] = "[data-details='selector-idpatient-details']"
            self.click_element(**param)

            lib_assert_data(updated_patient, self.patient_editor_fields, self.editor_config, self)

    @VTest.category('patient')
    @VTest.category('patient_editor')
    @VTest.category('save_option')
    @VTest.category('read_from_editor')
    @VTest.category('read_from_db')
    def when_POPULATING_and_SAVING_PATIENT_EDITOR_expect_to_retrieve_the_saved_patient_from_db(self):
        '''
        Steps:
        - go to some patient editor,
        - populate new random values,
        - click the save option,
        - read data of that patient from db,
        - go to that patient again from the main menu,
        - compare the retrieved values with the values on the screen.
        '''
        # Go to a random patref detail view
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        if patref_id:
            # Click on the Patient field to see the patient editor
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = "[data-details='selector-idpatient-details']"
            self.click_element(**param)
            lib_data_populate(self.patient_editor_fields, self.editor_config, self)
            lib_click_save_button(self)

            patref_json_data_from_db = self.get_object_data('patrefrequests/{0}/json'.format(str(int(patref_id.split('-')[-1]))))
            patient_id = patref_json_data_from_db["data"]["patrefrequests.idpatient"]
            patient_json_data_from_db = self.get_object_data('patients/{0}/json'.format(str(patient_id)))
            retrieved_patient = lib_data_retrieve_from_db(patient_json_data_from_db, self.patient_editor_fields)

            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="patRefsMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="allReferrals()"]'
            self.click_element(**param)
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": patref_id, "object_ids": patref_ids})
            # Click on the Patient field to see the patient editor
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = "[data-details='selector-idpatient-details']"
            self.click_element(**param)

            lib_assert_data(retrieved_patient, self.patient_editor_fields, self.editor_config, self, preprocessing="read_from_db")

VTest.add_test(testcase_patients())