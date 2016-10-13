from test_library import *
from vtest import *
import random
import datetime
import json
import time
from selenium.webdriver.common.keys import Keys

class testcase_patrefs(VTest):

    def __init__(self):
        self.grid_id = '#grid-patrefrequests'
        self.patref_detail_view_filename = "../client/app/secure/json/nchs/patrefrequests.json"
        self.patref_detail_view_fields = json.loads(open(self.patref_detail_view_filename, 'r').read())
        self.current_patref = str(VTest.test_value["patref"]["patref_providertrackingtag"][0])

        self.config = {
            "config_name": "patref_detail_view",
            "label_method": "css",
            "label_selector_pattern": "[data-details='{0}-details']",
            "input_method": "id",
            "input_selector_pattern": "{0}"
        }
        # When running a test method, the fail flag will be initialized to False, and change to True when a failure assertion is detected.
        self.fail = None
        self.log = []

    def helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(self, providertrackingtag, popupmenu):
        param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="patRefsMenu()"]'
        self.click_element(**param)
        param["selector"] = popupmenu
        self.click_element(**param)
        found, patref_ids = lib_find_object(providertrackingtag, self)
        return found

    @VTest.category('patref')
    @VTest.category('patref_detail_view')
    @VTest.category('patref_list_of_fields')
    def when_selecting_a_PATREF_DETAIL_VIEW_expect_to_see_a_LIST_OF_FIELDS_correctly(self):
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_patref = patref_id
        if patref_id:
            lib_check_list_of_fields(self.patref_detail_view_fields, self.config, self)

    @VTest.category('patref')
    @VTest.category('patref_detail_view')
    @VTest.category('save_option')
    def when_POPULATING_and_SAVING_PATREF_DETAILS_expect_to_see_the_save_and_refresh_option_work_well(self):
        '''
        Steps:
        - go to some patref detail view,
        - populate new random values,
        - store the new values in a variable,
        - click the save option,
        - compare the stored values with the refreshed values on the screen.
        '''
        # patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self, "patref_id": '', "patref_submenu": ''})
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_patref = patref_id
        if patref_id:
            lib_data_populate(self.patref_detail_view_fields, self.config, self)
            updated_patref = lib_read_data_from_editor_or_detail_view(self.patref_detail_view_fields, self.config, self)
            lib_click_save_button(self)
            lib_assert_data(updated_patref, self.patref_detail_view_fields, self.config, self)

    @VTest.category('patref')
    @VTest.category('patref_detail_view')
    @VTest.category('save_option')
    @VTest.category('read_from_editor')
    def when_POPULATING_and_SAVING_PATREF_DETAILS_expect_to_see_the_saved_patref_when_coming_from_the_main_menu(self):
        '''
        Steps:
        - go to some patref detail view,
        - populate new random values,
        - click the save option,
        - store the new values in a variable,
        - go to that patref detail view again from the main menu,
        - compare the stored values with the values on the screen.
        '''
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_patref = patref_id
        if patref_id:
            lib_data_populate(self.patref_detail_view_fields, self.config, self)
            lib_click_save_button(self)
            updated_patref = lib_read_data_from_editor_or_detail_view(self.patref_detail_view_fields, self.config, self)

            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="patRefsMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="allReferrals()"]'
            self.click_element(**param)
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": patref_id, "object_ids": patref_ids})
            lib_assert_data(updated_patref, self.patref_detail_view_fields, self.config, self)

    @VTest.category('patref')
    @VTest.category('patref_detail_view')
    @VTest.category('save_option')
    @VTest.category('read_from_db')
    def when_POPULATING_and_SAVING_PATREF_DETAILS_expect_to_retrieve_the_saved_patref_from_db(self):
        '''
        Steps:
        - go to some patref editor,
        - populate new random values,
        - click the save option,
        - read data of that patref from db,
        - go to that patref again from the main menu,
        - compare the retrieved values with the values on the screen.
        '''
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_patref = patref_id
        if patref_id:
            lib_data_populate(self.patref_detail_view_fields, self.config, self)
            lib_click_save_button(self)

            json_data_from_db = self.get_object_data('patrefrequests/{0}/json'.format(str(int(patref_id.split('-')[-1]))))
            retrieved_patref = lib_data_retrieve_from_db(json_data_from_db, self.patref_detail_view_fields)

            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="patRefsMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="allReferrals()"]'
            self.click_element(**param)

            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": patref_id, "object_ids": patref_ids})
            lib_assert_data(retrieved_patref, self.patref_detail_view_fields, self.config, self)

    @VTest.category('patref')
    @VTest.category('create_new_patref')
    def when_creating_REFERRAL_expect_to_see_that_referral_in_3_All_Referrals_and_3_My_Referrals_popup_menus(self):

        providertrackingtag, patient_id = lib_create_a_new_patref_picking_a_patient_randomly(self)
        self.current_patref = providertrackingtag

        popupmenu = '[ng-click="allReferrals()"]'
        if self.helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(providertrackingtag, popupmenu):
            self.log_assertion('The recently created patref appears in All Referrals popup menu correctly', True)
        else:
            self.log_assertion('The recently created patref does not appear in All Referrals popup menu"', False)

        popupmenu = '[ng-click="allNewReferrals()"]'
        if self.helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(providertrackingtag, popupmenu):
            self.log_assertion('The recently created patref appears in All Referrals > New popup menu correctly', True)
        else:
            self.log_assertion('The recently created patref does not appear in All Referrals > New popup menu"', False)

        popupmenu = '[ng-click="allOpenReferrals()"]'
        if self.helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(providertrackingtag, popupmenu):
            self.log_assertion('The recently created patref appears in All Referrals > Open Only popup menu correctly', True)
        else:
            self.log_assertion('The recently created patref does not appear in All Referrals > Open Only popup menu"', False)

        popupmenu = '[ng-click="myReferrals()"]'
        if self.helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(providertrackingtag, popupmenu):
            self.log_assertion('The recently created patref appears in My Referrals popup menu correctly', True)
        else:
            self.log_assertion('The recently created patref does not appear in My Referrals popup menu"', False)

        popupmenu = '[ng-click="myNewReferrals()"]'
        if self.helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(providertrackingtag, popupmenu):
            self.log_assertion('The recently created patref appears in My Referrals > New popup menu correctly', True)
        else:
            self.log_assertion('The recently created patref does not appear in My Referrals > New popup menu"', False)

        popupmenu = '[ng-click="myOpenReferrals()"]'
        if self.helper_check_if_RECENTLY_CREATED_PATREF_appears_in_some_popup_menu(providertrackingtag, popupmenu):
            self.log_assertion('The recently created patref appears in My Referrals > Open Only popup menu correctly', True)
        else:
            self.log_assertion('The recently created patref does not appear in My Referrals > Open Only popup menu"', False)

    @VTest.category('patref')
    @VTest.category('refresh_option')
    # def when_REFRESHING_a_PATREF_DETAIL_VIEW_expect_to_see_the_content_before_changing(self):
    def when_REFRESHING_a_PATREF_DETAIL_VIEW_expect_to_see_a_LIST_OF_FIELDS_correctly(self):
        patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_patref = patref_id
        if patref_id:
            lib_check_list_of_fields(self.patref_detail_view_fields, self.config, self)

            count = 10
            while count > 0:
                print "count: ", count
                count -= 1
                VTest.browser.refresh()
                lib_check_list_of_fields(self.patref_detail_view_fields, self.config, self)

VTest.add_test(testcase_patrefs())