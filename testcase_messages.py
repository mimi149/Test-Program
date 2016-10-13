from test_library import *
from vtest import *
import random
import datetime
import json
import time

class testcase_messages(VTest):

    def __init__(self):
        self.grid_id = "#grid-faxmessages"
        self.filename = "../client/app/secure/json/common/faxmessages.json"
        self.json_data = json.loads(open(self.filename, 'r').read())
        self.config = {
            "config_name": "faxmessage_detail_view",
            "label_method": "id",
            "label_selector_pattern": "{0}-label",
            "input_method": "id",
            "input_selector_pattern": "{0}-input"
        }
        self.next_button_selector = 'div#inboxForm div div section div.ui.compact.menu.toolbar div.right.menu.scanner.hasNext a.item i.fa.fa-chevron-right'
        self.previous_button_selector = 'div#inboxForm div div section div.ui.compact.menu.toolbar div.right.menu.scanner.hasPrev a.item i.fa.fa-chevron-left'
        self.log = []
        self.fail = False

    def helper_assign_to_a_random_user(self):
        '''
        :return: username of the assigned user if successfully, otherwise None.
        '''
        param = {"method": "id", "selector": "selector-idassigneduser-input", "popover_id": 'dropdown-overlay'}
        # Choose a random user
        users_from_editor = lib_get_items_from_selector(self, **param)
        user_display_names = [user.text for user in users_from_editor]

        if len(users_from_editor) > 0:

            item_index_to_select = random.randint(1, len(users_from_editor))

            # Select that random user
            param = {"method": "id", "selector": "selector-idassigneduser-input", "popover_id": "dropdown-overlay", "item_index_to_select": item_index_to_select}
            self.type_in_selector(**param)
            lib_click_save_button(self)

            # Get username of that assigned user
            users_from_db = self.get_object_data('vusers/val')
            index = 0
            try:
                while True:
                    if users_from_db["result"][index]["vusers._name"] == user_display_names[item_index_to_select-1]:
                        # The index of the selector starts from 1, while the
                        # index of the list users_from_editor starts from 0.
                        break
                    index += 1
            except:
                VTest.log_assertion(VTest(), 'index is out of range, cannot find user "' + user_display_names[item_index_to_select-1] + '" in db.', False)
                return None

            usr = users_from_db["result"][index]["vusers.username"]
            return usr
        else:
            return None

    def helper_change_message_status_to_archived(self, message_id):
        # Click the status selector
        param = {"method": "id", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = "selector-idfaxworkstatuscode-input"
        self.click_element(**param)
        item_index_to_select = 1 # STATUS = archived
        param = {"method": "id", "selector": "selector-idfaxworkstatuscode-input", "popover_id": "dropdown-overlay", "item_index_to_select": item_index_to_select}
        self.type_in_selector(**param)

        lib_click_save_button(self)

    def helper_check_if_message_in_My_Inbox_popup_menu(self, message_id):
        # go to user's inbox
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="myInbox()"]'
        self.click_element(**param)
        found, meassage_ids = lib_find_object(message_id, self)
        return found

    def helper_check_if_message_in_Archived_Messages_popup_menu(self, message_id):
        # go to Archived Messages popup menu
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="archivedMessages()"]'
        self.click_element(**param)
        found, meassage_ids = lib_find_object(message_id, self)
        return found

    def helper_check_if_message_in_Deleted_Messages_popup_menu(self, message_id):
        # Go to Deleted Messages popup menu
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="deletedMessages()"]'
        self.click_element(**param)
        found, meassage_ids = lib_find_object(message_id, self)
        return found

    def helper_check_if_ARCHIVED_MESSAGE_go_to_Archived_Messages_popup_menu(self):
        '''
        Is called when standing in a page showing a list of messages.
        Step:
        - pick some random message and go to its detail view,
        - call function to change status to archived,
        - call function to check if the message is in Archived Messages popup menu.
        '''
        message_id = lib_choose_and_go_to_a_random_object(self)
        if message_id:
            self.helper_change_message_status_to_archived(message_id)
            exist = self.helper_check_if_message_in_Archived_Messages_popup_menu(message_id)
            if exist:
                self.log_assertion('The assigned message come to Archived Messages popup menu correctly', True)
            else:
                self.log_assertion('The assigned message did not come to Archived Messages popup menu"', False)

    def helper_check_if_ASSIGNED_MESSAGE_go_to_My_Inbox_popup_menu(self):
        '''
        Is called when standing in a page showing a list of messages.
        Step:
        - pick some random message and go to its detail view,
        - call function to assign to some random user,
        - call function to check if the message is in his inbox.
        '''
        message_id = lib_choose_and_go_to_a_random_object(self)
        if message_id:
            usr = self.helper_assign_to_a_random_user()
            if usr:
                VTest.usr = usr
                VTest.pwd = VTest.get_pwd(usr)
                if not(self.login()):
                    exit(2)
                exist = self.helper_check_if_message_in_My_Inbox_popup_menu(message_id)
                if exist:
                    self.log_assertion('The assigned message come to "My Inbox" correctly', True)
                else:
                    self.log_assertion('The assigned message did not come to "My Inbox"', False)
            else:
                self.log_assertion('There is not any user to assign the message', True)

    def helper_check_if_DELETED_MESSAGE_go_to_Deleted_Messages_popup_menu(self, deleted=True):
        '''
        Is called when standing in a page showing a list of messages.
        Step:
        - pick some random message and go to its detail view,
        - open the deleting dialog and try to delete the message (deleted=True) or cancel (deleted=False)
        - call the function to check if the message is in Deleted Messages popup menu.
        :return: the id of the message to test for, or None if there is not any message to test for.
        '''
        message_id = lib_choose_and_go_to_a_random_object(self)
        if message_id:
            # Open the deleting dialog and submit or cancel
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = 'div#inboxForm div div section div div div.ui.top.dropdown.link.item i.fa.fa-gear'
            self.click_element(**param)
            param["selector"] = 'div#inboxForm div div section div div div div a.item i.fa.fa-times'
            self.click_element(**param)
            if deleted:
                param["selector"] = 'div.ui-dialog div.ui-dialog-buttonpane div.ui-dialog-buttonset button:nth-child(1) span'
                self.click_element(**param)
            else:
                param["selector"] = 'div.ui-dialog div.ui-dialog-buttonpane div.ui-dialog-buttonset button:nth-child(2) span'
                self.click_element(**param)

            exist = self.helper_check_if_message_in_Deleted_Messages_popup_menu(message_id)
            if deleted:
                if exist:
                    self.log_assertion('The deleted message come to Deleted Messages popup menu correctly', True)
                else:
                    self.log_assertion('The deleted message did not come to Deleted Messages popup menu', False)
            else:
                if exist:
                    self.log_assertion('The message come to Deleted Messages popup menu', False)
                else:
                    self.log_assertion('The message did not come to Deleted Messages popup menu', True)

            return message_id
        else:
            return None

    @VTest.category('message')
    @VTest.category('message_detail_view')
    @VTest.category('message_list_of_fields')
    def when_selecting_a_MESSAGE_DETAIL_VIEW_expect_to_see_a_LIST_OF_FIELDS_correctly(self):
        """
        This test runs for some message in Assigned Messages popup menu, it can run the same for other popup menu
        like My Inbox, Archived Messages, Deleted Messages, HID Inbox, ...

        Test the list of fields in a message detail view.
        """
        message_id, message_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_message = message_id
        if message_id:
            lib_check_list_of_fields(self.json_data, self.config, self)

    @VTest.category('message')
    @VTest.category('message_detail_view')
    @VTest.category('save_option')
    @VTest.category('populating')
    def when_POPULATING_and_SAVING_MESSAGE_DETAILS_expect_to_see_the_save_and_refresh_option_work_well(self):
        '''
        This test runs for some message in Assigned Messages popup menu, it can run the same for other popup menu
        like My Inbox, Archived Messages, Deleted Messages, HID Inbox, ...
        Steps:
        - go to some message detail view,
        - populate new random values,
        - store the new values in a variable,
        - click the save option,
        - compare the stored values with the refreshed values on the screen.
        '''
        message_id, message_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_message = message_id
        if message_id:
            lib_data_populate(self.json_data, self.config, self)
            updated_message = lib_read_data_from_editor_or_detail_view(self.json_data, self.config, self)
            lib_click_save_button(self)

            lib_assert_data(updated_message, self.json_data, self.config, self)

    @VTest.category('message')
    @VTest.category('message_detail_view')
    @VTest.category('save_option')
    @VTest.category('read_from_editor')
    @VTest.category('populating')
    def when_POPULATING_and_SAVING_MESSAGE_DETAILS_expect_to_see_the_saved_message_when_coming_from_the_main_menu(self):
        '''
        This test runs for some message in Assigned Messages popup menu, it can run the same for other popup menu
        like My Inbox, Archived Messages, Deleted Messages, HID Inbox, ...
        Steps:
        - go to some message detail view,
        - populate new random values,
        - click the save option,
        - store the new values in a variable,
        - go to that message again from the main menu,
        - compare the stored values with the values on the screen.
        '''
        message_id, message_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self, "submenu": '[ng-click="assignedMessages()"]'})
        self.current_message = message_id
        if message_id:
            lib_data_populate(self.json_data, self.config, self)
            lib_click_save_button(self)

            updated_message = lib_read_data_from_editor_or_detail_view(self.json_data, self.config, self)

            param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="messagesMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="assignedMessages()"]'
            self.click_element(**param)
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": message_id, "object_ids": message_ids})
            lib_assert_data(updated_message, self.json_data, self.config, self, preprocessing="read_from_editor")

    @VTest.category('message')
    @VTest.category('message_detail_view')
    @VTest.category('save_option')
    @VTest.category('read_from_db')
    @VTest.category('populating')
    def when_POPULATING_and_SAVING_MESSAGE_DETAILS_expect_to_retrieve_the_saved_message_from_db(self):
        '''
        This test runs for some message in Assigned Messages popup menu, it can run the same for other popup menu
        like My Inbox, Archived Messages, Deleted Messages, HID Inbox, ...
        Steps:
        - go to some message detail view,
        - populate new random values,
        - click the save option,
        - read data of that message from db,
        - go to that message again from the main menu,
        - compare the retrieved values with the values on the screen.
        '''
        message_id, message_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self, "submenu": '[ng-click="assignedMessages()"]'})
        self.current_message = message_id
        if message_id:
            lib_data_populate(self.json_data, self.config, self)
            lib_click_save_button(self)

            json_data_from_db = self.get_object_data('faxmessages/{0}/json'.format(message_id))
            retrieved_message = lib_data_retrieve_from_db(json_data_from_db, self.json_data)

            param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="messagesMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="assignedMessages()"]'
            self.click_element(**param)
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": message_id, "object_ids": message_ids})
            lib_assert_data(retrieved_message, self.json_data, self.config, self, preprocessing="read_from_db")

    @VTest.category('message')
    @VTest.category('message_detail_view')
    @VTest.category('next_and_previous_option')
    def when_going_to_other_message_and_go_back_expect_to_see_original_message(self):
        '''
        This test runs for some message in Assigned Messages popup menu, it can run the same for other popup menu
        like My Inbox, Archived Messages, Deleted Messages, HID Inbox, ...
        Steps:
        For each message in the list:
        - save the message data to a variable,
        - click the next option,
        - click the previous option,
        - compare the saved data with the data on the screen.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="assignedMessages()"]'
        self.click_element(**param)
        message_ids = lib_get_object_ids_from_grid(self)

        # Only test when the next and previous options are available.
        if len(message_ids) > 1:

            for i, message_id in enumerate(message_ids):
                param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
                param["selector"] = '[ng-click="messagesMenu()"]'
                self.click_element(**param)
                param["selector"] = '[ng-click="assignedMessages()"]'
                self.click_element(**param)
                lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": message_id, "object_ids": message_ids})
                original_message = lib_read_data_from_editor_or_detail_view(self.json_data, self.config, self)

                if i == 0:
                    # click the next button
                    param["selector"] = self.next_button_selector
                    self.click_element(**param)
                    # click the previous button
                    param["selector"] = self.previous_button_selector
                    self.click_element(**param)
                else:
                    # click the previous button
                    param["selector"] = self.previous_button_selector
                    self.click_element(**param)
                    # click the next button
                    param["selector"] = self.next_button_selector
                    self.click_element(**param)

                lib_assert_data(original_message, self.json_data, self.config, self)

    @VTest.category('message')
    @VTest.category('message_detail_view')
    @VTest.category('read_from_db')
    def when_RETRIEVING_MESSAGE_from_database_expect_to_see_the_correct_value_on_the_editor(self):
        '''
        This test runs for some message in Assigned Messages popup menu, it can run the same for other popup menu
        like My Inbox, Archived Messages, Deleted Messages, HID Inbox, ...
        Steps:
        For each message in the grid,
        - read data from db,
        - compare the data from db with the data on the screen.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="assignedMessages()"]'
        self.click_element(**param)
        message_ids = lib_get_object_ids_from_grid(self)

        for message_id in message_ids:
            param["selector"] = '[ng-click="messagesMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="assignedMessages()"]'
            self.click_element(**param)
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": self, "object_id": message_id, "object_ids": message_ids})

            json_data_from_db = self.get_object_data('faxmessages/{0}/json'.format(message_id))
            retrieved_message = lib_data_retrieve_from_db(json_data_from_db, self.json_data)

            lib_assert_data(retrieved_message, self.json_data, self.config, self, preprocessing="read_from_db")

    @VTest.category('message')
    @VTest.category('assigned_message')
    @VTest.category('message_assign/reassign')
    def when_REASSIGNING_some_random_ASSIGNED_MESSAGE_to_another_random_user_expect_that_message_go_to_his_inbox(self):
        '''
        Steps:
        - go to Assigned Messages popup menu,
        - call the helper function to pick some random assigned message, assign to some random user, go to his inbox to check the result.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="assignedMessages()"]'
        self.click_element(**param)
        self.helper_check_if_ASSIGNED_MESSAGE_go_to_My_Inbox_popup_menu()

    @VTest.category('message')
    @VTest.category('unassigned_message')
    @VTest.category('message_assign/reassign')
    def when_ASSIGNING_some_random_UNASSIGNED_MESSAGE_to_some_random_user_expect_that_message_go_to_his_inbox(self):
        '''
        Steps:
        - go to Unassigned Messages popup menu (HID Inbox),
        - call the helper function to pick some random unassigned message, assign to some random user, go to his inbox to check the result.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="hidInbox()"]'
        self.click_element(**param)

        self.helper_check_if_ASSIGNED_MESSAGE_go_to_My_Inbox_popup_menu()

    @VTest.category('message')
    @VTest.category('assigned_message')
    @VTest.category('message_change_status_to_archived')
    def when_changing_status_of_ASSIGNED_MESSAGE_to_ARCHIVED_expect_that_message_go_to_Archived_Messages_popup_menu(self):
        '''
        Steps:
        - go to Assigned Messages popup menu,
        - call the helper function to pick some random assigned message, change status to archived,
          go to Archived Messages popup menu to see the result.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="assignedMessages()"]'
        self.click_element(**param)
        self.helper_check_if_ARCHIVED_MESSAGE_go_to_Archived_Messages_popup_menu()

    @VTest.category('message')
    @VTest.category('unassigned_message')
    @VTest.category('message_change_status_to_archived')
    def when_changing_status_of_UNASSIGNED_MESSAGE__to_ARCHIVED_expect_that_message_go_to_Archived_Messages_popup_menu(self):
        '''
        Steps:
        - go to Unassigned Messages popup menu,
        - call the helper function to pick some random unassigned message, change status to archived,
          go to Archived Messages popup menu to see the result.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="hidInbox()"]'
        self.click_element(**param)
        self.helper_check_if_ARCHIVED_MESSAGE_go_to_Archived_Messages_popup_menu()

    @VTest.category('message')
    @VTest.category('assigned_message')
    @VTest.category('message_delete')
    def when_DELETING_some_random_ASSIGNED_MESSAGE_expect_that_message_go_to_Deleted_Messages_popup_menu(self):
        '''
        Steps:
        - go to Assigned Messages popup menu,
        - call the helper function to pick some random assigned message, delete that message and
          go to Deleted Messages popup menu to see the result.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="assignedMessages()"]'
        self.click_element(**param)
        self.helper_check_if_DELETED_MESSAGE_go_to_Deleted_Messages_popup_menu()

    @VTest.category('message')
    @VTest.category('assigned_message')
    @VTest.category('message_delete')
    def when_CANCELING_OF_DELETING_some_random_ASSIGNED_MESSAGE_expect_that_message_remain_undeleted(self):
        '''
        Steps:
        - go to Assigned Messages popup menu,
        - call the helper function to pick some random assigned message, open the deleting dialog but choose cancel,
          go to Deleted Messages popup menu to check the result.
        - go to Assigned Messages popup menu again to check if the message is still there.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="assignedMessages()"]'
        self.click_element(**param)
        message_id = self.helper_check_if_DELETED_MESSAGE_go_to_Deleted_Messages_popup_menu(deleted=False)

        if message_id:
            # Go to Assigned Messages popup menu again
            param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="messagesMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="assignedMessages()"]'
            self.click_element(**param)

            message_ids = lib_get_object_ids_from_grid(self)
            if message_id in message_ids:
                self.log_assertion('The deleting is canceled correctly', True)
            else:
                self.log_assertion('The deleting is not canceled correctly', False)

    @VTest.category('message')
    @VTest.category('unassigned_message')
    @VTest.category('message_delete')
    def when_DELETING_some_random_UNASSIGNED_MESSAGE_expect_that_message_go_to_Deleted_Messages_popup_menu(self):
        '''
        Steps:
        - go to Unassigned Messages popup menu,
        - call the helper function to pick some random unassigned message, delete that message and
          go to Deleted Messages popup menu to see the result.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="hidInbox()"]'
        self.click_element(**param)
        self.helper_check_if_DELETED_MESSAGE_go_to_Deleted_Messages_popup_menu()

    @VTest.category('message')
    @VTest.category('unassigned_message')
    @VTest.category('message_delete')
    def when_CANCELING_OF_DELETING_some_random_UNASSIGNED_MESSAGE_expect_that_message_remain_undeleted(self):
        '''
        Steps:
        - go to Unassigned Messages popup menu,
        - call the helper function to pick some random unassigned message, open the deleting dialog but choose cancel,
          go to Deleted Messages popup menu to check the result.
        - go to Unassigned Messages popup menu again to check if the message is still there.
        '''
        param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
        param["selector"] = '[ng-click="messagesMenu()"]'
        self.click_element(**param)
        param["selector"] = '[ng-click="hidInbox()"]'
        self.click_element(**param)
        message_id = self.helper_check_if_DELETED_MESSAGE_go_to_Deleted_Messages_popup_menu(deleted=False)

        if message_id:
            # Go to Unassigned Messages popup menu again
            param = {"method": "css", "description": "", "expected_browsed_url_pattern": None}
            param["selector"] = '[ng-click="messagesMenu()"]'
            self.click_element(**param)
            param["selector"] = '[ng-click="hidInbox()"]'
            self.click_element(**param)

            message_ids = lib_get_object_ids_from_grid(self)
            if message_id in message_ids:
                self.log_assertion('The deleting is canceled correctly', True)
            else:
                self.log_assertion('The deleting is not canceled correctly', False)

    @VTest.category('message')
    @VTest.category('refresh_option')
    # def when_REFRESHING_a_MESSAGE_DETAIL_VIEW_expect_to_see_the_content_before_changing(self):
    def when_REFRESHING_a_MESSAGE_DETAIL_VIEW_expect_to_see_a_LIST_OF_FIELDS_correctly(self):
        message_id, message_ids = lib_go_to_an_object_detail_view(**{"VTestObj": self})
        self.current_message = message_id
        if message_id:
            lib_check_list_of_fields(self.json_data, self.config, self)

            count = 10
            while count > 0:
                count -= 1
                VTest.browser.refresh()
                lib_check_list_of_fields(self.json_data, self.config, self)

VTest.add_test(testcase_messages())