from db_test import DB_test
from vtest import *
from selenium.webdriver.common.keys import Keys
import json

def lib_click_button_in_dialog(order_of_button, VTestObj):
    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = 'div.ui-dialog-buttonpane div.ui-dialog-buttonset button:nth-child({0}) span.ui-button-text'.format(str(order_of_button))
    VTestObj.click_element(**param)

def lib_click_save_button(VTestObj):
    param = {"method": "css", "selector": "[ng-show='toolconfig.save']", "description": None, "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

def lib_click_button_by_value(VTestObj, tag, value):
    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = "{0}[value=\"{1}\"]".format(tag, value)
    VTestObj.click_element(**param)

def lib_click_on_toolbar(VTestObj, tool):
    param = {"method": "css", "selector": "[ng-click=\"toolbar(\'{0}\')\"]".format(tool), "description": None, "expected_browsed_url_pattern": None}
    # param = {"method": "css", "selector": "[ng-show='toolconfig.coversheet']", "description": None, "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

def lib_click_submit_on_toolbar(VTestObj):
    param = {"method": "css", "selector": "[ng-click=\"toolbar('submit', 'portal')\"]", "description": None, "expected_browsed_url_pattern": None}
    # param = {"method": "css", "selector": "[ng-show='toolconfig.coversheet']", "description": None, "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

def lib_click_forwardto_button(VTestObj):
    param = {"method": "css", "selector": "[ng-click=\"toolbar(\'forwardto\')\"]", "description": None, "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

def lib_click_submit_button(VTestObj):
    param = {"method": "css", "selector": "[ng-click=\"toolbar(\'submit\', \'portal\')\"]", "description": None, "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

def lib_click_clone_button(VTestObj):
    param = {"method": "css", "selector": "[ng-show='toolconfig.clone']", "description": None, "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

def lib_click_addcover_button(VTestObj, checked=True):
    param = {"method": "id", "selector": "chkbx-addcover", "description": None, "expected_browsed_url_pattern": None}
    element = VTestObj.find_element(**param)
    if (checked and str(element.get_attribute('checked')).upper() != 'TRUE') or \
        (not checked and str(element.get_attribute('checked')).upper() == 'TRUE'):

        param = {"method": "css", "selector": "form#form-coveroptions div:nth-child(1) div:nth-child(2) div label span", "description": None, "expected_browsed_url_pattern": None}
        element = VTestObj.find_element(**param)
        element.click()

def lib_click_altcover_button(VTestObj, checked=True):
    param = {"method": "id", "selector": "chkbx-altcover", "description": None, "expected_browsed_url_pattern": None}
    element = VTestObj.find_element(**param)
    if (checked and str(element.get_attribute('checked')).upper() != 'TRUE') or \
        (not checked and str(element.get_attribute('checked')).upper() == 'TRUE'):

        if checked: # altcover can become True only when addcover is True
            lib_click_addcover_button(VTestObj, True)

        param = {"method": "css", "selector": "form#form-coveroptions div:nth-child(2) div:nth-child(2) div label span", "description": None, "expected_browsed_url_pattern": None}
        element = VTestObj.find_element(**param)
        element.click()

def lib_click_to_add_services_to_patref(VTestObj):

    param = {"method": "css", "selector": "ul#auth-accordian li:nth-child(3) section div:nth-child(2) table thead tr th ul li a[ng-click='showCodesets()']",
             "description": None, "expected_browsed_url_pattern": None}
    element = VTestObj.find_element(**param)
    element.click()

def lib_faxsubcategory_name_process(string):
    '''
    Remove category name from subcategory name
    '''
    pos = string.find("-")
    if pos != -1:
        string = string[pos+2:]
    return string

def lib_date_format_process(string, config_name=''):
    '''
    Remove time and change the date format
    '''
    if len(string) > 10:
        if config_name == 'patient_editor':
            string = datetime.datetime.strptime(string[:10], "%Y-%m-%d").__format__("%Y-%m-%d")
        else:
            string = datetime.datetime.strptime(string[:10], "%Y-%m-%d").__format__("%m/%d/%Y")
    return string

def lib_phone_number_format_process(string):
    '''
    Remove the country code
    '''
    if len(string) == 11:
        string = string[1:]
    return string

def lib_filename_process(string):
    '''
    Remove the path from filename
    '''
    return string.split('/')[-1]

def lib_get_object_ids_from_grid(VTestObj):
    '''
    :return: a list of object ids from the current page
    '''
    objects = VTestObj.find_elements_by_css_selector(VTestObj.grid_id + ' div:nth-child(2) table.k-selectable tbody tr')

    object_ids = []
    for row_number in range(len(objects)):
        object_ids.append(objects[row_number].text.split()[0])
    if len(object_ids) <= 0:
        VTest.log_assertion(VTestObj, 'The grid contains no object', True)

    return object_ids

def lib_go_to_object_editor_or_detail_view(**kw):
    '''
    Is called when standing in some grid showing a list of objects.
    '''
    VTestObj = kw.get("VTestObj", "")
    object_id = kw.get("object_id", None)
    object_ids = kw.get("object_ids", None)

    object_id = str(object_id)
    if not object_ids:
        # Get a list of objects on the current page
        object_ids = lib_get_object_ids_from_grid(VTestObj)
    VTestObj.log_step('lib_go_to_object_editor_or_detail_view: ' + object_id)
    row_number = object_ids.index(object_id) + 1 # list index starts from 0, while row number starts from 1

    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = VTestObj.grid_id + ' div:nth-child(2) table.k-selectable tbody tr:nth-child({0}) td:nth-child(1) a span'.format(row_number)
    VTestObj.click_element(**param)

def lib_choose_and_go_to_a_random_object(VTestObj):
    object_ids = lib_get_object_ids_from_grid(VTestObj)
    object_id = None
    if len(object_ids) > 0:
        # Choose a random object and go to its editor or detail view
        object_id = str(object_ids[random.randint(0, len(object_ids)-1)])
        lib_go_to_object_editor_or_detail_view(**{"VTestObj": VTestObj, "object_id": object_id, "object_ids": object_ids})
    return object_id

def lib_get_items_from_selector(VTestObj, **kw):
    '''
    :method and selector: for selecting the textbox of the selector
    :return: a list of items' values of a selector
    '''
    method = kw["method"]
    selector = kw["selector"]
    popover_id = kw["popover_id"]

    # Click the textbox to see the dropdown list.
    param = {"method": method, "selector": selector, "caller": "lib_get_items_from_selector"}

    if 'selector' in VTest.log_list:
        VTestObj.log_for_element(**param)

    param = {"method": method, "selector": selector, "description": "", "expected_browsed_url_pattern": None}
    VTestObj.click_element(**param)

    items = VTestObj.find_elements_by_css_selector('#' + popover_id + ' > .selector-overlay-body > li')

    if len(items) <= 0:
        VTest.log_assertion(VTestObj, 'The selector contains no item', False)

    return items

def lib_type_to_find_object_in_grid(object_id, VTestObj):

    method = "css"
    selector = VTestObj.grid_id + " div div table thead tr th:nth-child(1) div.v-widget.v-with-icon input.column-filter"
    param = {"method":method, "selector": selector}
    element = VTestObj.find_element(**param)
    element.clear()
    element.send_keys(object_id)
    element.send_keys(Keys.RETURN)
    time.sleep(1)

def lib_find_object(object_id, VTestObj):
    lib_type_to_find_object_in_grid(object_id, VTestObj)
    object_ids = lib_get_object_ids_from_grid(VTestObj)
    found = object_id in object_ids
    return found, object_ids

def lib_read_data_from_editor_or_detail_view(fields, config, VTestObj):
    """
    Is called whenever we want to read the current values in the input fields on the screen
    """
    data = {}
    for field in fields:
        if field["for_test"]["viewtype"] == "" or field["for_test"]["viewtype"] == "Hidden":
            continue
        # if field.get("label", "") == "Rendering": # need to be processed individually, code will be written later
        #     continue
        method = config["input_method"]
        selector = config["input_selector_pattern"].format(str(field['id']))

        param = {"method":method, "selector": selector}
        element = VTestObj.find_element(**param)

        data[str(field["label"])] = element.get_attribute('value')

    return data

def lib_data_retrieve_from_db(json_data_from_db, fields):
    """
    Retrieve data from database.
    """
    data_from_db = json_data_from_db["data"]

    data = {}
    for field in fields:
        if field["for_test"]["viewtype"] == "" or field["for_test"]["viewtype"] == "Hidden":
            continue
        if field.get("label", "") == "Rendering": # need to be processed individually, code will be written later
            continue

        # The key "obj" exists in the field means that the value of that field is just the id,
        # we need to get the name associated with that id.
        if not field.get("valrouteTname"):
            value = data_from_db[field["tname"] + "." + field["vidfield"]]

            # The None value in database is equivalent to the "" value in the editor.
            if value == None:
                value = ""
        else:
            obj_name = field["valrouteTname"]
            id = data_from_db[field["tname"] + "." + field["vidfield"]]
            data_associated_with_id = VTest.get_object_data('{0}/{1}/json'.format(obj_name, id))
            if data_associated_with_id:
                value = data_associated_with_id["data"][field["valrouteTname"]+"._name"]
            else:
                value = ""

        data[field["label"]] = str(value)
    return data

def lib_check_list_of_fields(fields, config, VTestObj):
    for i, field in enumerate(fields):

        if field["for_test"]["viewtype"] == "Hidden":
            continue

        if field["for_test"].get("label_selector", "") != "":
            method = str(field["for_test"]["label_selector"]["method"])
            selector = str(field["for_test"]["label_selector"]["selector"])
        else:
            method = config["label_method"]
            selector = config["label_selector_pattern"].format(field['id'])

        expected_value = field["label"]
        desc = 'to confirm that "{0}" field is present at position #{1}'.format(field["label"], i+1)
        VTestObj.assert_element_text(method, selector, expected_value, desc)

def lib_data_populate(fields, config, VTestObj):
    """
    Calls type_in_fields and type_in_selector to populate some new data.
    """
    for field in fields:
        if field["for_test"]["readonly"] != "TRUE":
            method = config["input_method"]
            selector = config["input_selector_pattern"].format(field['id'])

            updated_data = ''
            if field["for_test"]["viewtype"] == "text":
                updated_data = str(field["for_test"]["text_to_type"])

                param = {"method": method, "selector": selector, "text_to_type": updated_data}
                VTestObj.type_in_field(**param)

            if field["for_test"]["viewtype"] == "dropdown":

                popover_id = 'dropdown-overlay'
                item_index_to_select = 0
                # Count the number of items and select a random item.
                param = {"method": method, "selector": selector, "popover_id": popover_id}
                item_number = len(lib_get_items_from_selector(VTestObj, **param))
                if item_number > 0:
                    item_index_to_select = random.randint(1, item_number)

                # Process individual case for message - BEGIN -------------
                if field["for_test"].get("preprocessing") and \
                        "not_automatically_populate_assigned_value" in field["for_test"]["preprocessing"]:
                    # avoid the first value (the "assigned" value)
                    if item_number > 1:
                        item_index_to_select = random.randint(2, item_number)
                    else:
                        item_index_to_select = 0
                # Process individual case for message - END ----------------

                if item_index_to_select > 0:
                    param = {"method": method, "selector": selector, "popover_id": popover_id}

                    # For testing the selector with data retrieved from patrefrequests.json and faxmessages.json (2016/02/23):
                    expected_match_count = field["for_test"].get("expected_match_count", '')

                    if expected_match_count != '':
                        param["text_to_type"] = str(field["for_test"]["text_to_type"])
                        expected_match_count = int(expected_match_count)
                        if item_index_to_select > expected_match_count:
                            item_index_to_select = random.randint(1, expected_match_count)

                        param["expected_match_count"] = expected_match_count
                    # --------------------------------------------------------------------------------------------------------

                    param["item_index_to_select"] = item_index_to_select

                    updated_data = VTestObj.type_in_selector(**param)

            # Log the updated value.
            param = {}
            param["VTestObj"] = VTestObj
            param["config"] = config
            param["field_name"] = str(field["label"])
            param["value"] = updated_data
            lib_log_updated_value(**param)

def lib_data_populate_from_test_value(**kw):
    """
    Calls type_in_fields and type_in_selector to populate some new data.
    Data is read from test_value.json.
    """
    fields = kw["fields"]
    data_position = kw["data_position"]
    config = kw["config"]
    data = kw["data"]
    VTestObj = kw["VTestObj"]

    for field in fields:
        if field["for_test"]["readonly"] != "TRUE":
            label = str(field["label"])
            method = config["input_method"]
            selector = config["input_selector_pattern"].format(field['id'])
            param = {"method": method, "selector": selector}
            pos = data_position[label] if data_position.get(label, '') else 0
            param["text_to_type"] = str(data[label][pos])

            updated_data = param["text_to_type"]
            if field["for_test"]["viewtype"] == "text":
                VTestObj.type_in_field(**param)

            elif field["for_test"]["viewtype"] == "dropdown":
                param["popover_id"] = 'dropdown-overlay'
                param["item_index_to_select"] = 1
                # param["expected_match_count"] = 1
                updated_data = VTestObj.type_in_selector(**param)

            # Log the updated value.
            param = {}
            param["VTestObj"] = VTestObj
            param["config"] = config
            param["field_name"] = label
            param["value"] = updated_data
            lib_log_updated_value(**param)

def lib_assert_data(object, fields, config, VTestObj, preprocessing=None):
    """
    Calls assert_field_text() for each field of the editor or the detail view.
    @object: the object which contains the values needed to be compared with
    the values of the current object on the editor or the detail view.
    """
    for field in fields:
        if field["for_test"]["viewtype"] == "" or field["for_test"]["viewtype"] == "Hidden":
            continue
        # if field.get("label", "") == "Rendering": # need to be processed individually, code will be written later
        #     continue
        config_name = config["config_name"]
        method = config["input_method"]
        selector = config["input_selector_pattern"].format(field['id'])
        expected_value = object.get(str(field["label"]), None)

        if expected_value:

            if field["for_test"].get("preprocessing") and "faxsubcategory name process" in field["for_test"]["preprocessing"]:
                # Remove the category name (for read_from_editor)
                if preprocessing in ["read_from_editor"]:
                    expected_value = lib_faxsubcategory_name_process(expected_value)

            if field["for_test"].get("preprocessing") and "date reformat" in field["for_test"]["preprocessing"]:
                # Reformat the date (for read_from_db)
                if preprocessing in ["read_from_db"]:
                    expected_value = lib_date_format_process(expected_value, config_name)

            if field["for_test"].get("preprocessing") and "phone number reformat" in field["for_test"]["preprocessing"]:
                # Reformat the phone number (for read_from_db)
                if preprocessing in ["read_from_db"]:
                    expected_value = lib_phone_number_format_process(expected_value)

            if field["for_test"].get("preprocessing") and "filename process" in field["for_test"]["preprocessing"]:
                # Remove the path (for read_from_db)
                if preprocessing in ["read_from_db"]:
                    expected_value = lib_filename_process(expected_value)

            VTestObj.assert_field_text(method, selector, expected_value)

def lib_go_to_an_object_detail_view(**kw):
    VTestObj = kw.get("VTestObj", "")
    object_id = kw.get("object_id", None)
    submenu = kw.get("submenu", None)

    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}

    if hasattr(VTestObj, "config") and VTestObj.config["config_name"] == "faxmessage_detail_view":
        # For message detail view
        param["selector"] = '[ng-click="messagesMenu()"]'
        VTestObj.click_element(**param)
        param["selector"] = submenu if submenu else '[ng-click="hidInbox()"]'
        VTestObj.click_element(**param)
    else:
        # For patref detail view and patient editor
        # (For going to a patient editor, first go to a patref detail view, then click on the Patient field to see the patient editor)
        param["selector"] = '[ng-click="patRefsMenu()"]'
        VTestObj.click_element(**param)
        param["selector"] = submenu if submenu else '[ng-click="allReferrals()"]'
        VTestObj.click_element(**param)

    object_ids = None
    if object_id == None:
        # Choose a random object
        object_ids = lib_get_object_ids_from_grid(VTestObj)
        if len(object_ids) > 0:
            object_id = object_ids[random.randint(0, len(object_ids)-1)]
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": VTestObj, "object_id": object_id, "object_ids": object_ids})
        else:
            return None, None
    else:
        found, object_ids = lib_find_object(object_id, VTestObj)
        if found:
            lib_go_to_object_editor_or_detail_view(**{"VTestObj": VTestObj, "object_id": object_id, "object_ids": object_ids})
        else:
            return None, None

    return object_id, object_ids

def lib_go_to_a_patient_detail_view(VTestObj, patient_id=None):
    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = '[ng-click="patientsMenu()"]'
    VTestObj.click_element(**param)

    param["selector"] = '[ng-click="findPatient()"]'
    VTestObj.click_element(**param)

    patient_ids = None
    if patient_id == None:
        # Choose a random patient
        param = {"method": 'id', "selector": 'selector-find', "popover_id": 'dropdown-overlay-popover'}
        patients = lib_get_items_from_selector(VTestObj, **param)
        patient_number = len(patients)
        if patient_number > 0:
            item_index_to_select = random.randint(1, patient_number)
            if item_index_to_select > 0:
                param = {"method": 'id', "selector": 'selector-find', "popover_id": 'dropdown-overlay-popover', "item_index_to_select": item_index_to_select}
                VTestObj.type_in_selector(**param)
            # Select the View Patient button to go to a patient detail view
            param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
            param["selector"] = 'div.ui-dialog div.ui-dialog-buttonpane div.ui-dialog-buttonset button:nth-child(2) span'
            VTestObj.click_element(**param)

            return patients[item_index_to_select - 1] # list index starts from 0, while row number in selector starts from 1
        return None
    else:
        param = {"method": "id", "selector": "selector-find", "popover_id": "dropdown-overlay-popover", "item_index_to_select": 1}

        # Find patient
        sql = { "query": "select lastname from patients where idpatient={0};".format(patient_id)}
        sql["args"] = []
        result = DB_test.db_CRUD([sql], VTest.db_connection)
        if len(result) != 1:
            VTestObj.log_assertion('Patient with id = ' + str(patient_id) + ' not found.', False)
            return None
        last_name = result[0][0]
        param["text_to_type"] = last_name
        param["item_index_to_select"] = 1
        VTestObj.type_in_selector(**param)

        # Select the View Patient button to go to a patient detail view
        param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
        param["selector"] = 'div.ui-dialog div.ui-dialog-buttonpane div.ui-dialog-buttonset button:nth-child(2) span'
        VTestObj.click_element(**param)
    return patient_id

def lib_select_a_random_item_in_selector(method, selector, popover_id, VTestObj):
    param = {"method": method, "selector": selector, "popover_id": popover_id}
    items = lib_get_items_from_selector(VTestObj, **param)
    item_number = len(items)
    if item_number > 0:
        item_index_to_select = random.randint(1, item_number)
        if item_index_to_select > 0:
            param = {"method": method, "selector": selector, "popover_id": popover_id, "item_index_to_select": item_index_to_select}
            VTest.type_in_selector(VTestObj, **param)

        return items[item_index_to_select - 1], items # list index starts from 0, while row number in selector starts from 1
    return None, None

def lib_process_date_value(date):
    return str(datetime.datetime.strptime(date, "%m/%d/%Y").date())

def lib_process_null_value(sql, columns):
    for column in columns:
        oldstr = column + "=''"
        if sql.find(oldstr) != -1:
            newstr = "(" + column + "='' or " + column + " is null)"
            sql = sql.replace(oldstr, newstr)
    return sql

def lib_find_patient_info(patient_id):
    '''
    Must return exact one patient, otherwise None return means failure
    '''
    sql = {"query": "select lastname, firstname, middlename, dob, mrn from patients where idpatient = {0};".format(patient_id)}
    sql["args"] = []
    result = DB_test.db_CRUD([sql], VTest.db_connection)
    if len(result) == 1:
        patient = {"lastname": result[0][0]}
        patient["firstname"] = result[0][1]
        patient["middlename"] = result[0][2]
        patient["DOB"] = result[0][3]
        patient["mrn"] = result[0][4]
        return patient
    return None

def lib_find_patient_id(data):
    '''
    Must return exact one patient, otherwise None return means failure
    '''
    sql = {}
    if data.get("DOB"):
        data["DOB"] = lib_process_date_value(data["DOB"])

    sql["query"] = "select idpatient from patients where lastname='{0}' and firstname='{1}' and middlename='{2}' and date(dob)='{3}' and mrn='{4}';"\
                    .format(data["lastname"], data["firstname"], data["middlename"], data["DOB"], data["mrn"])

    sql["query"] = lib_process_null_value(sql["query"], data.keys())

    sql["args"] = []
    result = DB_test.db_CRUD([sql], VTest.db_connection)
    if len(result) == 1:
        return result[0][0]
    return None

def lib_find_patient_id_of_patref(providertrackingtag):
    sql = {}
    sql["query"] = "select idpatient from patrefrequests where providertrackingtag ='{0}';"
    sql["args"] = [providertrackingtag]
    result =  DB_test.db_CRUD([sql], VTest.db_connection)
    try:
        return result[0][0]
    except:
        return None

def lib_find_recently_created_patref_of_patient(patient_id):
    '''
    Must return exact one patref, otherwise None return means failure
    '''
    sql = {}
    sql["query"] = "select providertrackingtag, cstamp from patrefrequests where idpatient ={0} order by cstamp desc limit 1;"
    sql["args"] = [patient_id]
    result =  DB_test.db_CRUD([sql], VTest.db_connection)
    if result != [] and result[0][1].date() == datetime.date.today(): # check cstamp to be sure this is the recently created patref.
        return result[0][0] # providertrackingtag
    return None

def lib_get_selector(**kw):

    VTestObj = kw.get("VTestObj", '')
    obj_kind = kw.get("obj_kind", '')
    view_kind = kw.get("view_kind", '')
    field_name = kw.get("field_name", '')
    input_or_label = kw.get("input_or_label", '')

    if obj_kind == 'patref':
        fields = VTestObj.patref_detail_view_fields
        config = VTestObj.config
    elif obj_kind == 'patient':
        if view_kind == 'detail_view':
            fields = VTestObj.patient_detail_view_fields
            config = VTestObj.detail_view_config
        elif view_kind == 'editor':
            fields = VTestObj.patient_editor_fields
            config = VTestObj.editor_config

    id = ''
    for field in fields:
        if field["label"].upper() == field_name.upper():
            if field["for_test"].get("label_selector", "") != "":
                method = str(field["for_test"]["label_selector"]["method"])
                selector = str(field["for_test"]["label_selector"]["selector"])
            else:
                id = str(field["id"])
                if input_or_label == 'label':
                    method = config["label_method"]
                    selector = config["label_selector_pattern"].format(id)
                elif input_or_label == 'input':
                    method = config["input_method"]
                    selector = config["input_selector_pattern"].format(id)
            break
    return method, selector

def lib_log_updated_value(**kw):

    config = kw["config"]
    if config["config_name"] != "patref_detail_view":
        return # Will add for faxmessage detail view and patient editor later

    field_name = kw["field_name"]
    value = kw["value"]
    VTestObj = kw["VTestObj"]

    with open(VTestObj.updated_value_filename) as infile:
        jsontext = json.load(infile)

    patref_providertrackingtag = VTestObj.current_patref

    if VTest.sanity_test_step > 0:
        step = "sanity test step " + str(VTest.sanity_test_step)
        if not jsontext.get(step, None):
            jsontext[step] = {}
        if not jsontext[step].get(patref_providertrackingtag, None):
            jsontext[step][patref_providertrackingtag] = {}
        jsontext[step][patref_providertrackingtag][field_name] = value
    else:
        if not jsontext.get(patref_providertrackingtag, None):
            jsontext[patref_providertrackingtag] = {}
        jsontext[patref_providertrackingtag][field_name] = value

    with open(VTestObj.updated_value_filename, "w") as outfile:
        json.dump(jsontext, outfile, indent=4)

def lib_add_services(**kw):
    VTestObj = kw["VTestObj"]
    number = kw.get("number", 1)
    from_test_value = kw.get("from_test_value", False)
    data = kw.get("data", None)

    # Click on Services field in the patref detail view
    param = {"method": 'css', "selector": "li#services-tab header div div label[ng-click='showDetail()'"}
    VTestObj.click_element(**param)
    time.sleep(1)

    # Click on the Plus sign
    lib_click_to_add_services_to_patref(VTestObj)
    time.sleep(3)
    new_services = []

    if from_test_value:
        data = data["Services"]
        if number[0] > len(data):
            VTestObj.log_assertion('Invalid number of Services.', False)
            return
        if number[0] + number[1] -1 > len(data):
            number[1] = len(data) - number[0]

        for i in range(number[0], number[0] + number[1]):
            param = {"method": 'id', "selector": 'search_code2', "text_to_type": str(data[i])}
            VTestObj.type_in_field(**param)
            time.sleep(1)

            param = {"method": 'css', "selector": "table#grid-services tbody tr:nth-child(1) td:nth-child(1) input[type='checkbox']"}
            try:
                element = VTestObj.find_element(**param)
                if not element.is_selected():
                    VTestObj.click_element(**param)
                    param = {"method": 'css', "selector": "table#grid-services tbody tr:nth-child(1) td:nth-child(2)"}
                    element = VTestObj.find_element(**param)
                    new_services.append(element.text)
                else:
                    VTestObj.log_assertion('Service ' + str(data[i]) + ' already exists.', True)
            except:
                VTestObj.log_assertion('Service ' + str(data[i]) + ' not found.', False)

    else: # select randomly
        step = 0
        for i in range(number[1]):
            service_number = (random.randint(1, 11) + step) % 10 + 1
            param = {"method": 'css', "selector": "table#grid-services tbody tr:nth-child({0}) td:nth-child(1) input[type='checkbox']".format(service_number)}
            element = VTestObj.find_element(**param)
            if not element.is_selected():
                VTestObj.click_element(**param)
                param = {"method": 'css', "selector": "table#grid-services tbody tr:nth-child({0}) td:nth-child(2)".format(service_number)}
                element = VTestObj.find_element(**param)
                new_services.append(element.text)

            step = random.randint(1, 10)

    time.sleep(3)
    VTestObj.click_element(**{"method": 'id', "selector": 'btnAddServicesClose'})

    # Log the updated value.
    param = {}
    param["VTestObj"] = VTestObj
    param["config"] = VTestObj.test_patref_obj.config
    if from_test_value:
        param["field_name"] = "Services picking from test_value.json"
    else:
        param["field_name"] = "Services picking randomly"
    param["value"] = new_services
    lib_log_updated_value(**param)

def lib_select_corresponding_ICD(VTestObj, new_ICD9s):

    try: # case of more than 1 corresponding ICD9
        param = {"method": 'css', "selector": "table#cross-diags-10to9 tbody tr td:nth-child(2) div div ul li:nth-child(1)"}
        element9 = VTestObj.find_element(**param)
        new_ICD9s.append(element9.text.split(':')[0])
        param = {"method": 'css', "selector": "table#cross-diags-10to9 tbody tr td:nth-child(2) div div ul li:nth-child(1) input[type='radio']"}
    except: # case of only 1 corresponding ICD9
        param = {"method": 'css', "selector": "table#cross-diags-10to9 tbody tr"}
        element9 = VTestObj.find_element(**param)
        new_ICD9s.append(element9.text.split('\n')[1].split(':')[0])
        param = {"method": 'css', "selector": "table#cross-diags-10to9 tbody tr td:nth-child(2) div div input[type='radio']"}

    VTestObj.click_element(**param)
    time.sleep(2)

    # Click Add button
    VTestObj.click_element(**{"method": 'id', "selector": 'btn-add10to9'})
    time.sleep(1)
    return new_ICD9s

def lib_add_Diagnoses_ICD(**kw):
    VTestObj = kw["VTestObj"]
    number = kw.get("number", None)
    from_test_value = kw.get("from_test_value", False)
    data = kw.get("data", None)

    # Click on Diagnoses ICD9/ ICD10
    param = {"VTestObj": VTestObj.test_patref_obj, "obj_kind": 'patref', "field_name": 'Diagnoses ICD9', "input_or_label": 'label'}
    method, selector = lib_get_selector(**param)
    param = {"method": method, "selector": selector}
    VTestObj.click_element(**param)

    # Click on Plus sign of ICD10
    param = {"method": 'css'}
    param["selector"] = 'ul#auth-accordian li#diagnoses-tab section div table:nth-child(2) thead tr th ul li:nth-child(1) a i.fa.fa-plus-square'
    VTestObj.click_element(**param)
    time.sleep(3)
    new_ICD10s = []
    new_ICD9s = []

    if from_test_value:
        data = data["Diagnoses ICD10"]
        if number[0] > len(data):
            VTestObj.log_assertion('Invalid number of Diagnoses.', False)
            return
        if number[0] + number[1] - 1 > len(data):
            number[1] = len(data) - number[0]

        for i in range(number[0], number[0] + number[1]):
            param = {"method": 'id', "selector": 'search_code10', "text_to_type": str(data[i])}
            time.sleep(1)
            VTestObj.type_in_field(**param)
            time.sleep(1)

            param = {"method": 'css', "selector": "table#grid-diag10s tbody tr:nth-child(1) td:nth-child(1) input[type='checkbox']"}
            try:
                element = VTestObj.find_element(**param)
            except:
                VTestObj.log_assertion('ICD ' + str(data[i]) + ' not found.', True)
                continue

            if not element.is_selected():
                VTestObj.click_element(**param)
                time.sleep(2)
                param = {"method": 'css', "selector": "table#grid-diag10s tbody tr:nth-child(1) td:nth-child(2)"}
                element10 = VTestObj.find_element(**param)
                new_ICD10s.append(element10.text)

                new_ICD9s = lib_select_corresponding_ICD(VTestObj, new_ICD9s)
            else:
                VTestObj.log_assertion('ICD ' + str(data[i]) + ' already exists.', True)

    else: # select randomly
        step = 0
        for i in range(number[1]):
            ICD_number = (random.randint(1, 11) + step) % 10 + 1
            param = {"method": 'css', "selector": "table#grid-diag10s tbody tr:nth-child({0}) td:nth-child(1) input[type='checkbox']".format(ICD_number)}
            element = VTestObj.find_element(**param)

            if not element.is_selected():
                VTestObj.click_element(**param)
                time.sleep(2)
                param = {"method": 'css', "selector": "table#grid-diag10s tbody tr:nth-child({0}) td:nth-child(2)".format(ICD_number)}
                element10 = VTestObj.find_element(**param)
                new_ICD10s.append(element10.text)

                new_ICD9s = lib_select_corresponding_ICD(VTestObj, new_ICD9s)

            step = random.randint(1, 10)

    time.sleep(3)
    # lib_clic+k_button_in_dialog(1, VTestObj)
    VTestObj.click_element(**{"method": 'id', "selector": 'btnGenerateModalClose'})

    # Log the updated value.
    param = {}
    param["VTestObj"] = VTestObj
    param["config"] = VTestObj.test_patref_obj.config
    if from_test_value:
        param["field_name"] = "Diagnoses ICD picking from test_value.json"
    else:
        param["field_name"] = "Diagnoses ICD picking randomly"
    new_ICDs = {}
    if new_ICD9s != []:
        new_ICDs["ICD9"] = new_ICD9s
    if new_ICD10s != []:
        new_ICDs["ICD10"] = new_ICD10s
    param["value"] = new_ICDs
    lib_log_updated_value(**param)

# id,search_code2 type_in_field
# css, "table#grid-services tbody tr td input[type='checkbox']" check

# ul#auth-accordian li:nth-child(2) ICD 9/10
# ul#auth-accordian li:nth-child(2) section div table:nth-child(1) thead tr th ul li a i.fa.fa-plus-square -->Plus sign of ICD9
# ul#auth-accordian li:nth-child(2) section div table:nth-child(2) thead tr th ul li a i.fa.fa-plus-square -->Plus sign of ICD10
# ul#auth-accordian li:nth-child(3) Services
# ul#auth-accordian li:nth-child(3) section div:nth-child(2) table thead tr th ul li a i.fa.fa-plus-square
# ul#auth-accordian li:nth-child(4) Notes/Attachments

def lib_create_a_new_patref_by_creating_a_new_patient(VTestObj, data_position=0):
    '''
    Create a new patient, then a new patref for that patient.
    '''
    new_last = str(VTestObj.test_value["patient_editor"]["LAST NAME"][data_position])
    new_first = str(VTestObj.test_value["patient_editor"]["FIRST NAME"][data_position])
    new_DOB = str(random.randint(1,12)).zfill(2) + '/' + str(random.randint(1,28)).zfill(2) + '/' + str(1930+random.randint(1,85))

    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = '[ng-click="patRefsMenu()"]'
    VTestObj.click_element(**param)
    param["selector"] = '[ng-click="createPatientReferral()"]'
    VTestObj.click_element(**param)

    # selectors for the fields are copied from selector_fort_test.json ("CREATE_PATIENT_REFERRALS_DIALOG")
    param = {"method": "id", "selector": "patients.lastname-input", "text_to_type": new_last}
    VTestObj.type_in_field(**param)
    param = {"method": "id", "selector": "patients.firstname-input", "text_to_type": new_first}
    VTestObj.type_in_field(**param)
    param = {"method": "id", "selector": "patients.dob-input", "text_to_type": new_DOB}
    VTestObj.type_in_field(**param)

    lib_click_button_in_dialog(2, VTestObj)

    data = {"lastname": new_last, "firstname": new_first, "DOB": new_DOB, "middlename": '', "mrn": ''}
    patient_id = lib_find_patient_id(data)
    providertrackingtag = lib_find_recently_created_patref_of_patient(patient_id)
    if not providertrackingtag:
        VTestObj.log_assertion('Cannot find the recently created patref in db', False)
    else:
        # Update the current patref and patient.
        VTestObj.current_patref = providertrackingtag
        VTestObj.patient = {"patient id": patient_id, "firstname": new_first, "lastname": new_last, "DOB": new_DOB}

        # Log the new patref
        param = {"field_name": "Created for patient"}
        param["value"] = VTestObj.patient
        param["VTestObj"] = VTestObj
        param["config"] = VTestObj.test_patref_obj.config
        lib_log_updated_value(**param)

def lib_create_a_new_patref_for_a_patient(VTestObj, patient_id): # Cannot be used

    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = '[ng-click="patRefsMenu()"]'
    VTestObj.click_element(**param)
    param["selector"] = '[ng-click="createPatientReferral()"]'
    VTestObj.click_element(**param)

    patient = lib_find_patient_info(patient_id)

    if patient == None:
        VTestObj.log_assertion('Cannot find the patient in db with the id = ' + str(patient_id), False)
    else:
        param = {"method": "id", "selector": "patients.lastname-input", "text_to_type": patient["lastname"]}
        VTestObj.type_in_field(**param)
        param = {"method": "id", "selector": "patients.firstname-input", "text_to_type": patient["firstname"]}
        VTestObj.type_in_field(**param)
        param = {"method": "id", "selector": "patients.middlename-input", "text_to_type": patient["middlename"]}
        VTestObj.type_in_field(**param)
        param = {"method": "id", "selector": "patients.dob-input", "text_to_type": patient["DOB"]}
        VTestObj.type_in_field(**param)
        param = {"method": "id", "selector": "patients.mrn-input", "text_to_type": patient["mrn"]}
        VTestObj.type_in_field(**param)

        # Click Save button
        lib_click_button_in_dialog(2, VTestObj)

        providertrackingtag = lib_find_recently_created_patref_of_patient(patient_id)
        if not providertrackingtag:
            VTestObj.log_assertion('Cannot find the recently created patref in db', False)

        return providertrackingtag, patient_id

def lib_create_a_new_patref_picking_a_patient_randomly(VTestObj):

    param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
    param["selector"] = '[ng-click="patRefsMenu()"]'
    VTestObj.click_element(**param)
    param["selector"] = '[ng-click="createPatientReferral()"]'
    VTestObj.click_element(**param)

    dlg_fields = VTestObj.selector_json["CREATE_PATIENT_REFERRALS_DIALOG"]

    method = str(dlg_fields["selector"]["method"])
    selector = str(dlg_fields["selector"]["selector"])
    popover_id= str(dlg_fields["selector"]["popover_id"])
    patient, patients = lib_select_a_random_item_in_selector(method, selector, popover_id, VTestObj)

    if patient:
        data = {}
        for field in dlg_fields["detail"]:
            param = {"method": str(field["method"]), "selector": str(field["selector"])}
            element = VTestObj.find_element(**param)
            data[str(field["key"])] = element.get_attribute('value')

        # Click Save button
        lib_click_button_in_dialog(2, VTestObj)

        patient_id = lib_find_patient_id(data)
        if not patient_id:
            VTestObj.log_assertion('Cannot find the patient in db with the data from the Create Patient Referrals dialog', False)

        providertrackingtag = lib_find_recently_created_patref_of_patient(patient_id)
        if not providertrackingtag:
            VTestObj.log_assertion('Cannot find the recently created patref in db', False)

        return providertrackingtag, patient_id
    else:
        VTestObj.log_assertion('There is not any patient in the Create Patient Referrals dialog', False)

def lib_go_to_a_patient_detail_view_from_a_patref_detail_view(VTestObj, patref):
    patref_id, patref_ids = lib_go_to_an_object_detail_view(**{"VTestObj": VTestObj.test_patref_obj, "patref_id": patref, "patref_submenu": ''})

    # Click the blue icon
    time.sleep(2)
    param = {"method": 'css', "selector": "ul#auth-accordian li#auth-summary header div:nth-child(3) div:nth-child(1) div:nth-child(2) div.selector-view-patient"}
    VTestObj.click_element(**param)

def lib_select_receiver_in_coversheet_dialod(VTestObj, receivers, data_position=0):
    # The selector in this dialog works unstably, so need to try several times by the two loops.
        receiver = str(receivers[data_position])
        count = 0
        found = False
        while count < 5 and not found:
            param = {"method": 'id', "selector": 'toname-search'}
            VTestObj.click_element(**param)

            param["method"] = 'css'
            param["selector"] = 'form#form-coveroptions div:nth-child(3) div:nth-child(2) div div'
            element = VTestObj.find_element(**param)

            if element.text:
                items = element.text.split('\n')
                for item_index_to_select in range(len(items)):
                    if items[item_index_to_select].find(receiver) != -1:
                        found = True
                        break

                if found:
                    print 'item_index_to_select: ', item_index_to_select
                    count2 = 0
                    while count2 < 5:
                        items = VTest.browser.find_elements_by_css_selector('div.tt-suggestion')
                        print 'items: ', items
                        if items == []:
                            count2 += 1
                            # Click the selector again
                            param = {"method": 'id', "selector": 'toname-search'}
                            element = VTestObj.find_element(**param)
                            element.clear()
                            VTestObj.click_element(**param)
                        else:
                            items[item_index_to_select].click()
                            time.sleep(1)
                            # Successfully selected the receiver, so click the Ok button to close the dialog
                            lib_click_button_by_value(VTestObj, 'input', 'OK')

                            # Log the updated value
                            param = {}
                            param["VTestObj"] = VTestObj
                            param["config"] = VTestObj.test_patref_obj.config
                            param["field_name"] = "Send Fax to in coversheet"
                            param["value"] = str(receivers[data_position])
                            lib_log_updated_value(**param)
                            break
                else:
                    VTest.log_assertion(VTestObj, 'The expected receiver ' + receiver + ' cannot be found in the Coversheet dialog.', False)
                    return

            else:
                count += 1
