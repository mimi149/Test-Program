import glob
import httplib
import re
import time
import inspect
import traceback
import json
import datetime
import textwrap
import sys
import os
import random
#import psycopg2
import subprocess
from sys import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from db_test import DB_test


def get_caller(depth):
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, depth)
    return caller_frame[1][3]

class VTest:

    def __init__(self):
        # When running a test method, the fail flag will be initialized to False, and change to True when a failure assertion is detected.
        self.fail = None
        self.log = []

    def login_user(self, usr=None, pwd=None, description=None, exception_raise=True):
        """
        Login to the system using the credentials provided.
        This method is used for workflow tests to simulate
        multiple users using the system
        """
        if not(description is None):
            self.log_step("Logging in as '" + usr +"' "+ description + "\n")

        if not(self.login(usr, pwd, description, exception_raise)):
            if exception_raise:
                # Fail by triggering the exception ...
                raise Exception('login error')
            else:
                return False

        # Expect ot be at /auth/g/12/u/8/f/all/8
        #m = re.search('/auth/g/(.*)/u/(.*)/f/all/(.*)$', VTest.browser.current_url)
        # Expect ot be at /patref/g/12/u/8/f/all/8
        # m = re.search('/patref/g/(.*)/u/(.*)/f/all/(.*)$', VTest.browser.current_url)
        # VTest.group_id = m.group(1)
        # VTest.user_id = m.group(2)
        return True

    def goto_url(self, relative_url, description=None):
        """
        Allows specifying the relative URL we are browsing to.
        Parses the JSON and returns an instantiated object.
        @param desc: A string describing the location we are going to, e.g. "the patients details page".
        @param relative_url: A string specifying the destination URL.
        """
        VTest.browser.get(VTest.base_url + relative_url)
        description_str = description + ': ' if description is not None else ''
        self.log_step('Browsed to ' + description_str + VTest.base_url + relative_url)
        time.sleep(1)
        return

    def find_elements_by_css_selector(self, selector):
        param = {"method": "css", "selector": selector, "caller": "find_elements_by_css_selector"}
        if 'find' in VTest.log_list:
            self.log_for_element(**param)
        return VTest.browser.find_elements_by_css_selector(selector)

    def find_element_by_css_selector(self, selector):
        param = {"method": "css", "selector": selector, "caller": "find_element_by_css_selector"}
        if 'find' in VTest.log_list:
            self.log_for_element(**param)
        return VTest.browser.find_element_by_css_selector(selector)

    def find_element(self, **kw):
        """
        Find an element based on the selector type.
        @param method: The interpretation of the selector. Currently supports 'id','css','dialog-button'.
        @param selector: The selector for locating the element.
        @rtype : element
        """
        method = kw["method"]
        selector = kw["selector"]
        assert isinstance(method, str)
        assert isinstance(selector, str)
        param = {"method": method, "selector": selector, "caller": "find_element"}
        if 'find' in VTest.log_list:
            self.log_for_element(**param)
        element = None
        if method == 'id':
            element = VTest.browser.find_element_by_id(selector)
        elif method == 'css':
            element = VTest.browser.find_element_by_css_selector(selector)
        elif method == 'dialog-button':
            #return ValerTest.browser.find_elements_by_css_selector('span.ui-button-text:contains(' + selector + ')')
            element = VTest.browser.find_elements_by_xpath('//button/span[contains(text(),"' + selector + '")]')
        else:
            raise Exception('Lookup method ' + method + ' not supported.')

        # Full set of options supported by selenium:
        #
        #find_elements_by_name
        #find_elements_by_xpath
        #find_elements_by_link_text
        #find_elements_by_partial_link_text
        #find_elements_by_tag_name
        #find_elements_by_class_name
        #find_elements_by_css_selector

        if isinstance(element, list):
            if len(element) > 0:
                element = element[0]
            else:
                element = None

            assert_pass = True if element else False
            assert_msg = 'Find '
            assert_msg += description if description is not None else 'element'
            assert_msg += ' ("' + method + ':' + selector + '")'
            self.log_assertion(assert_msg, assert_pass)

        return element

    # def click_or_hover_element(self, option="click", method, selector, description=None, expected_browsed_url_pattern=None, selector2=None):
    def click_or_hover_element(self, **kw):
        """
        @type method: str
        @type selector: str
        @type description: str
        @type expected_browsed_url_pattern: regex string
        """
        option = kw["option"]
        method = kw["method"]
        selector = kw["selector"]
        selector2 = kw.get("selector2", '')
        description = kw.get("description", '')
        expected_browsed_url_pattern = kw.get("expected_browsed_url_pattern", '')

        assert_pass = True

        if option!='click' and option!='hover' and option!='hover_then_click':
            raise Exception('click_or_hover_element option error')
        element = None
        VTest.browser.save_screenshot(VTest.test_result_folder + '\\' + 'screenie_before_find_element_in_click_or_hover.png')
        retry = 5
        while retry > 0:
            retry -= 1
            try:
                param = {"method": method,  "selector": selector}
                element = self.find_element(**param)
                break
            except:
                pass
            time.sleep(0.5)

        element2 = None
        if option=='hover_then_click' and selector2 is not None:
            param["selector"] = selector2
            element2 = self.find_element(**param)
            if element2 is None:
                raise Exception("Hover-then-Click cannot find element2.")

        if isinstance(element, list):
            if len(element) > 0:
                element = element[0]
            else:
                element = None
        VTest.browser.save_screenshot(VTest.test_result_folder + '\\' + 'screenie_before_click_in_click_or_hover.png')

        if element is not None:
            element_text = element.text
            if option=='hover_then_click':
                retry = 5
                while retry > 0:
                    retry -= 1
                    try:
                        VTest.mouse.move_to_element(element).perform()
                        time.sleep(0.5)
                        element2.click()
                        break
                    except:
                        pass
                    time.sleep(0.5)

            elif option=='click':
                try:
                    element.click()
                except:
                    assert_pass = False
                    assert_msg = option + 'ed '
                    assert_msg += description if description is not None else 'element'
                    assert_msg += ' ("' + method + ':' + selector + '")'
                    self.log_assertion(assert_msg, assert_pass)
                    self.log_exception(traceback.format_exc())

            elif option=='hover':
                VTest.mouse.move_to_element(element).perform()

            if assert_pass:
                time.sleep(0.5)
                assert_msg = option + 'ed '
                assert_msg += description if description is not None else 'element'
                assert_msg += ' ("' + method + ':' + selector + '")'

                if expected_browsed_url_pattern is not None:
                    regexp = re.compile(expected_browsed_url_pattern.replace('{id}', element_text))
                    rel_url = VTest.browser.current_url[VTest.browser.current_url.index('#!/') + 2:999]
                    assert_pass = regexp.match(rel_url)
                    assert_msg += ' and browsed to "' + rel_url + '" as expected by "' + expected_browsed_url_pattern + '".' if assert_pass \
                        else ' and browsed to "' + rel_url + '" incorrectly; expected "' + expected_browsed_url_pattern + '".'
                else:
                    assert_msg += '; skipping URL validation.'

                self.log_assertion(assert_msg, assert_pass)

        else:
            self.log_assertion('Could not find element ("' + method + ':' + selector + '").', False)
        return

    # def click_element(method, selector, description=None, expected_browsed_url_pattern=None):
    def click_element(self, **kw):
        kw["option"] = "click"
        self.click_or_hover_element(**kw)

    # def hover_click_element(selector2, method, selector, description=None, expected_browsed_url_pattern=None):
    def hover_click_element(self, **kw):
        kw["option"] = "hover_then_click"
        self.click_or_hover_element(**kw)

    def type_in_selector(self, **kw):
        """
        Types in the selector to filter the results.
        Verifies that the number of matches is as expected.
        Selects the specified item and verifies that the selection is as expected.
        """
        method = kw.get("method", '')
        selector = kw.get("selector", '')
        text_to_type = kw.get("text_to_type", '')
        timeout = kw.get("timeout", 3)
        popover_id = kw.get("popover_id", 'dropdown-overlay-popover')
        expected_match_count = kw.get("expected_match_count", None)
        item_index_to_select = kw.get("item_index_to_select", 1)
        expected_selection_pattern = kw.get("expected_selection_pattern", None)
        description = kw.get("description", '')
        clear = kw.get("clear", True)

        param = {"method": method, "selector": selector, "caller": "type_in_selector"}
        if 'type' in VTest.log_list:
            self.log_for_element(**param)

        element = None
        if method == 'id':
            element = VTest.browser.find_element_by_id(selector)
        elif method == 'css':
            element = VTest.browser.find_element_by_css_selector(selector)
        if isinstance(element, list):
            if len(element) > 0:
                element = element[0]
            else:
                element = None
        if element is not None:
            if clear and text_to_type:

                count = 0
                item_text = ''
                while item_text.find(text_to_type.upper()) == -1 and count < 5:
                    # element.click()
                    element.clear()
                    element.send_keys(text_to_type)
                    time.sleep(2)
                    try:
                        first_item = self.find_element_by_css_selector('#' + popover_id + ' > .selector-overlay-body > li:nth-child(1)')
                        item_text = first_item.text.upper()
                    except:
                        pass
                    count += 1

                print '\ncount: ', count - 1, ', selector: ', selector
                if count >= 5:
                    VTest.log_assertion(self, "The filter in the selector " + selector + " doesn't work", True)

            # element.send_keys(Keys.RETURN)

            time.sleep(timeout)
            items = VTest.browser.find_elements_by_css_selector('#' + popover_id + ' > .selector-overlay-body > li')

            print 'Number of items in the selector: ', len(items), ', selector: ', selector, ', text_to_type: ', text_to_type, '\n'

            if expected_match_count is not None:
                assert isinstance(expected_match_count, int)
                try:
                    if description:
                        self.log_step(description)
                    if isinstance(items, list):
                        if len(items) == expected_match_count:
                            self.log_assertion('Selector match count for "' + text_to_type + '" is ' + str(
                                expected_match_count) + ' as expected.', True)
                        else:
                            self.log_assertion('Selector match count for "' + text_to_type + '" is ' + str(
                                len(items)) + ' is incorrect; expected ' + str(expected_match_count) + '.', False)

                except:
                    self.log_assertion('Selector match count for "' + text_to_type + '" is *zero*; expected ' + str(
                        expected_match_count) + '.', False)
            else:
                self.log_assertion('Skipping selection count validation.', True)

            # If the total matches are smaller than index of item to be selected, then report the error and fail
            if len(items) < item_index_to_select:
                print 'number of items: ', len(items)
                self.log_assertion('for ' + (description if description else '') + ', item_index_to_select=' + str(item_index_to_select) + ' > the number of items in the filter=' + str(len(items)) + ':  ' + str(traceback.format_exc()), False)
                return

            # If the total matches expected are smaller than the index, then report the user error and fail
            if expected_match_count is not None and item_index_to_select > expected_match_count:
                self.log_assertion('for ' + (description if description else '') + ', item_index_to_select=' + str(item_index_to_select) + ' is greater than expected_match_count=' + str(expected_match_count) + ':  ' + str(traceback.format_exc()), False)
                return

            item = self.find_element_by_css_selector('#' + popover_id + ' > .selector-overlay-body > li:nth-child(' + str(item_index_to_select) + ')')

            if item is not None:
                item_text = item.text
                try:
                    item.click()
                except:
                    pass
                time.sleep(1)
                assert_pass = True
                assert_msg = 'Selected dropdown item ' + str(item_index_to_select) + ':"' + item_text + '"'
                if expected_selection_pattern is not None:
                    regexp = re.compile(expected_selection_pattern)
                    assert_pass = regexp.match(item_text)
                    assert_msg += ' as expected by "' + expected_selection_pattern + '".' if assert_pass \
                        else ' incorrectly; expected "' + expected_selection_pattern + '".'
                else:
                    assert_msg += '; Skipping selection pattern validation.'
                self.log_assertion(assert_msg, assert_pass)
                return item_text
            else:
                self.log_assertion(traceback.format_exc(), False)
        return

    def type_in_field(self, **kw):
        """
        Type text in a form field
        @rtype : None
        @type description: basestring
        """
        method = kw.get("method", '')
        selector = kw.get("selector", '')
        text_to_type = kw.get("text_to_type", '')
        description = kw.get("description", '')
        clear = kw.get("clear", True)

        param = {"method": method, "selector": selector, "caller": "type_in_field"}
        if 'type' in VTest.log_list:
            self.log_for_element(**param)

        param = {"method":method, "selector": selector}
        element = self.find_element(**param)
        if clear:
            element.clear()
        assert isinstance(text_to_type, str)
        element.send_keys(text_to_type)
        step_description = 'Typed text "' + text_to_type + '"'
        assert isinstance(description, str)
        step_description += ' ' + description + '.' if description else '.'
        self.log_step(step_description)
        return

    def assert_element_text(self, method, selector, expected_value, description=None):
        param = {"method": method, "selector": selector, "caller": "assert_element_text"}
        if 'assertion' in VTest.log_list:
            self.log_for_element(**param)
        param = {"method":method, "selector": selector}
        element = self.find_element(**param)
        description_str = description + ' - ' if description is not None else ''
        if element is None:
            self.log_assertion(description_str + 'cannot find of element ' + method + ': "' + selector + '".', False)
        if element.text[:len(expected_value)].upper() == expected_value.upper():
            self.log_assertion(description_str + 'content of element ' + method + ': "' + selector + '" is "' + expected_value + '" as expected.', True)
        else:
            self.log_assertion(description_str + 'content of element ' + method + ': "' + selector + '" is "' + element.text + '" but expected "' + expected_value + '".', False)
        return

    def assert_field_text(self, method, selector, expected_value, description=None):
        param = {"method": method, "selector": selector, "caller": "assert_field_text"}
        if 'assertion' in VTest.log_list:
            self.log_for_element(**param)
        param = {"method":method, "selector": selector}
        element = self.find_element(**param)
        description_str = description + ' - ' if description is not None else ''
        if element is None:
            self.log_assertion(description_str + 'cannot find of element ' + method + ': "' + selector + '".', False)
        if element.get_attribute('value')[:len(expected_value)].upper() == expected_value.upper():
            self.log_assertion(description_str + 'content of element ' + method + ': "' + selector + '" is "' + expected_value + '" as expected.', True)
        else:
            self.log_assertion(description_str + 'content of element ' + method + ': "' + selector + '" is "' + element.get_attribute('value') + '" but expected "' + expected_value + '".', False)
        return

    def log_assertion(self, message, passed):
        """
        @rtype : void
        """
        logmsg = 'passed - ' if passed else 'failed - '
        logmsg += message
        logmsg = logmsg.split(';')[0]
        self.log.append(LogEntry('assertion', logmsg))
        if not passed:
            filename = ''.join(map(lambda x:x if x not in "\\/:*?\"'<>|#- $%@&*()+!^," else '.', logmsg))
            filename = 'assertion' + '-' + filename
            VTest.browser.save_screenshot(VTest.test_result_folder + '\\' + filename + ".png")
        self.fail = self.fail or not passed
        return

    def log_exception(self, exception):
        """
        Add a log entry with a type of 'exception' and a message passed in via the exception parameter.
        @exception : string
        """
        assert isinstance(exception, str)
        self.log.append(LogEntry("exception", exception))
        if len(self.log) > 0:
            message = self.log[-1].message
            print self.log[-1].type, ' ', message
            filename = ''.join(map(lambda x:x if x not in "\\/:*?\"'<>|#- $%@&*()+!^," else '.', message))
            filename = "exception" + '-' + self.log[-1].type + '-' + filename
            try:
                VTest.browser.save_screenshot(VTest.test_result_folder + '\\' + filename + ".png")
            except:
                pass
        self.fail = True
        return

    def log_for_element(self, **kw):
        method = kw["method"]
        selector = kw["selector"]
        caller = kw["caller"]
        msg = caller + ": " + method + ", " + selector
        self.log_step(msg)
        if caller.split('_')[0] != 'assert':
            print  'caller: ' + caller + ', method: ' + method + ', selector: ' + selector
            filename = ''.join(map(lambda x:x if x not in "\\/:*?\"'<>|#- $%@&*()+!^," else '.', selector))
            filename = caller + "-" + method + "-" + filename
            VTest.browser.save_screenshot( VTest.test_result_folder + '\\' + filename + ".png")

    def log_step(self, message):
        self.log.append(LogEntry('step', message))
        return

    def run(self):
        """
        Runs all test methods in this test case class.
        A method is regarded a test method if it starts with "when_" and contains "_expect_" in its name.
        @param self: An instance of the test-case class inheriting from VTest.
        """
        VTest.need_to_print_header = True
        for name, function in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith('when_') and '_expect_' in name:

                if VTest.parallel:
                    if VTest.should_test_method_run(VTest(), name):
                        item_name = VTest.queue_in + '\\' + self.__class__.__name__ + '.' + name
                        if not(os.path.isfile(item_name)):
                            open(item_name, 'w').close()
                else:

                    # Initialize for each function to run
                    self.fail = None
                    self.log = []

                    try:
                        # If all categories are requested, then
                        if VTest.cat_list is None:
                            # We need to print the test case header when running the first method for this class
                            if VTest.need_to_print_header:
                                print '\n\n    testcase:"' + self.__class__.__name__ + '": \n'
                                VTest.need_to_print_header = False
                            # When executing in parallel, we need to create files in the queue_in folder.
                            # The names of the files represent the names of functions which will be called
                            # by the subprocesses when they are invoked later.
                            else:
                                # In normal execution mode
                                if VTest.mode is None:
                                    # Invoke the test method
                                    function()
                                # In plan execution mode, we only print out the test method name.
                                elif VTest.mode == 'plan':
                                    print '        ' + name
                                # To avoid duplicate calls, we do not need to call done() for wrappers; they call it themselves.
                                # We only call done() in normal mode, after invocation occurs; in other modes we do not invoke the test method.
                                if VTest.mode is None and function.__name__ != 'wrapper':
                                    # Specify the name of the test method which completed.
                                    self.done(name)
                            # When specific category filters are requested
                        else:
                            # When specific categories are selected, only wrappers need to execute; non-wrappers are intended to be excluded.
                            if function.__name__ == 'wrapper':
                                function()
                    except:
                        #e = sys.exc_info()[0]
                        #print "Exception:", e
                        # Log the exception and continue with next method.
                        self.log_exception(traceback.format_exc())
                        self.done(name)

        time.sleep(1)
        return

    def done(self, caller=None):
        if caller is None:
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 3)
            caller = calframe[1][3]
        if self.fail:
            print '        ' + caller + ': failed'
            print

            if VTest.export:
                VTest.export_method(self.__class__.__name__, caller, 'failed', '')
            self.log.append(LogEntry('End', '-- end fail log.'))

            DB_test.db_test_result_update(VTest.detail_report, caller, self.fail, self.log)

            for event in self.log:
                event.message = event.message.encode('ascii', 'ignore')
                prefix = '            '
                if event.type is not None:
                    prefix += str(event.type) + ': '
                if event.message is not None:
                    logstr = event.message
                else:
                    logstr = '.'
                wrapper = textwrap.TextWrapper(initial_indent=prefix, width=128,
                                               subsequent_indent=' ' * len(prefix))
                print wrapper.fill(logstr)
                print

                if VTest.export:
                    event_type = event.type
                    event_message = event.message.replace('"', '""')
                    if event.type == 'assertion':
                        event_type = 'passed' if event.message.startswith('passed') else 'failed'
                        event_message = event.message[9:] if event.message is not None else ''
                    export_wrapper = textwrap.TextWrapper(initial_indent='', width=99999, subsequent_indent=' ' * len(prefix))
                    VTest.export_method(self.__class__.__name__, caller, event_type, export_wrapper.fill(event_message))
        else:
            print '        ' + caller + ': passed'
            print

            DB_test.db_test_result_update(VTest.detail_report, caller, self.fail, self.log)

            if VTest.export:
                VTest.export_method(self.__class__.__name__, caller, 'passed', '')

        # Re-initiate to prepare for the next testcase
        self.get_browser_and_mouse()
        if not(self.login()):
            exit(2)

        return

    def run_all(self):
        """
        Run all tests found in the VTest.tests list.
        All parameterization is defined statically on VTest and consumed by the various downstream methods.
        """
        header_line = 'label:"' + VTest.label + '"' if VTest.label is not None else ''
        header_line += ' timestamp:"' + VTest.timestamp + '"\n git:"' + VTest.git + '": '
        print header_line
        # When in export mode, create the export file and populate the header
        if VTest.export and not(VTest.parallel):
            VTest.export_file = open(VTest.export_filename, 'w')
            VTest.export_file.write('"Label", "Git", "Timestamp", "Test Case", "Test Method", "Category", "Event", "Message"\n')
            VTest.export_file.close()
        if len(VTest.tests) == 0:
            print 'No tests to run!'
            return

        if not VTest.mode and not VTest.parallel:
            self.get_browser_and_mouse()
            if not(self.login()):
                exit(2)

        for test in VTest.tests:
            test.run()

        # Close the browser after all tests completed.
        try:
            VTest.browser.quit()
        except:
            pass
        return

    def run_from_queue(self, id_testrun, parallel_idx):
        if parallel_idx > 0:
            print 'Running background test process #' + str(parallel_idx) + ' for id_testrun = ' + str(id_testrun) + '.\n'
        time.sleep(5)
        time.sleep(random.randint(3, 15))

        filenames = glob.glob(VTest.queue_in + "/*")
        print '\n ................... Number of files: ', len(filenames)

        self.get_browser_and_mouse()
        if not(self.login()):
            exit(2)

        while len(filenames) > 0:
            try:
                f = filenames[0].split('.')
                class_name = f[0][9:]
                method_name = f[1]
                in_file_name = filenames[0]
                out_file_name = in_file_name.replace(VTest.queue_in, VTest.queue_out)
                not_run_file_name = in_file_name.replace(VTest.queue_in, VTest.not_test_now)

                TestClass = getattr(sys.modules[class_name], class_name)
                test = TestClass()

                method = getattr(test, method_name)

            except: # Remove the invalid method if exists.
                if os.path.isfile(in_file_name):
                    os.remove(in_file_name)
                time.sleep(5)
                filenames = glob.glob(VTest.queue_in + "/*")
                print '\n ................... Number of files: ', len(filenames)
                continue

            if VTest.should_test_method_run(VTest(), method_name):

                try:
                    if os.path.isfile(out_file_name):
                        os.remove(in_file_name)
                    else:
                        os.rename(in_file_name, out_file_name)
                except:
                    pass
                print "\n run: ", method_name
                # Initialize for each function to run
                test.fail = False
                test.log = []
                # try:
                print 'running: ', method_name
                method()
                # except:
                #     test.log_exception(traceback.format_exc())
                # test.done(name)

            else:
                try:
                    if os.path.isfile(not_run_file_name):
                        os.remove(in_file_name)
                    else:
                        os.rename(in_file_name, not_run_file_name)
                except:
                    pass
                print "\n not run: ", method_name

            time.sleep(5)
            filenames = glob.glob(VTest.queue_in + "/*")
            print '\n ................... Number of files: ', len(filenames)

        try:
            VTest.browser.quit()
        except:
            pass
        raw_input('End of subprocess #' + str(parallel_idx) + ' for id_testrun = ' + str(id_testrun) +
                  '\n Enter a key to close the terminal.')
        return

    def login(self, usr=None, pwd=None, description=None, exception_raise=True):
        """
        Login to the system using the static credentials.
        When a login failure is detected it aborts the tests.
        """
        # VTest.parallel_idx > 0 means it's a subprocess in parellel running, we always use the default usr and pwd.'
        if usr is None or VTest.parallel_idx > 0:
            usr = VTest.usr
            pwd = VTest.pwd
        else:
            if pwd is None:
                pwd = VTest.get_pwd(usr)
        # print 'login with: ', usr, ', ', pwd

        retry = 3
        while retry > 0:
            retry -= 1
            try:
                try:
                    VTest.browser.find_element_by_css_selector('a[ng-click="logout()"]').click()
                except:
                    pass
                if not VTest.browser:
                    self.get_browser_and_mouse()
                if not 'login' in VTest.browser.current_url:
                    VTest.browser.get(VTest.login_url)
                param = {"method": "id", "selector": "login-name", "caller": "login"}
                if 'login' in VTest.log_list:
                    self.log_for_element(**param)
                element = VTest.browser.find_element_by_id('login-name')
                element.clear()
                element.send_keys(usr)
                VTest.browser.find_element_by_id('login-password').send_keys(pwd)
                VTest.browser.find_element_by_id('login-button').click()
                time.sleep(0.5)

                # print "\n VTest.browser.current_url after login: ", VTest.browser.current_url

                if 'login' in VTest.browser.current_url:
                    print 'Could not login; try different credentials.'
                    self.get_browser_and_mouse()
                else:
                    # Expect ot be at /auth/g/12/u/8/f/all/8
                    # m = re.search('/auth/g/(.*)/u/(.*)/f/all/(.*)$', VTest.browser.current_url)
                    # m = re.search('/patref/g/(.*)/u/(.*)/f/all/(.*)$', VTest.browser.current_url)
                    # VTest.group_id = m.group(1)
                    # VTest.user_id = m.group(2)
                    # VTest.browser.save_screenshot(VTest.test_result_folder + '\\' + 'screenie_after_login_success.png')
                    return True
            except:
                pass
        try:
            VTest.browser.save_screenshot(VTest.test_result_folder + '\\' + 'screenie_of_login_fail.png')
            VTest.browser.quit()
        except:
            pass
        return False

    def get_browser_and_mouse(self):
        try:
            VTest.browser.quit()
        except:
            pass
        if VTest.browser_name.lower() == "phantomjs":
            VTest.browser = webdriver.PhantomJS()
            VTest.browser.set_window_size(1920, 1080)
        else: # default: VTest.browser_name= "chrome":
            VTest.browser = webdriver.Chrome()
        VTest.mouse = webdriver.ActionChains(VTest.browser)

    def should_test_method_run(self, name=None):
        """
        Checked whether a method should execute based on its category association.
        This method is only used within the category decorator.
        @param name: The name of the method being run.
        @rtype : True if the test method should execute; False otherwise.
        """
        method_name = name if name is not None else get_caller(2)
        if VTest.cat_list is None:
            return True
        else:
            for requested_cat in VTest.cat_list:
                for method_cat in VTest.categories[method_name]:
                    if method_cat == requested_cat:
                        return True
        return False


    # Globals used across all test case instances

    @staticmethod
    def init():
        """
        Initialize the VTest attributes
        """
        VTest.timestamp = str(datetime.datetime.now())

        VTest.queue_in = 'queue_in'
        VTest.not_test_now = 'queue_in_not_test'
        VTest.queue_out = 'queue_out'

        VTest.db_connection = "host='localhost' port='5432' dbname='valer_nchs' user='postgres' password=''"
        VTest.browser_name = "chrome"
        VTest.browser = None
        VTest.mouse = None

        if platform == "linux" or platform == "linux2":
            VTest.is_linux = True # linux
        elif platform == "darwin":
            VTest.is_linux = True # OS X
        elif platform == "win32":
            VTest.is_linux = False # Windows

        #: The git description is computed once across all tests.
        cwd = os.getcwd()
        os.chdir('../')
        git_hash = VTest.run_command('git describe --always').split('-')[-1]
        git_branch = VTest.run_command('git rev-parse --abbrev-ref HEAD')
        VTest.git = str(git_branch) + ':' + str(git_hash)
        os.chdir(cwd)

        #: The connection information is common to all tests.
        VTest.tapi_host = 'vm.test.com'
        VTest.tapi_port = 5010
        VTest.app_host = 'vm.test.com'
        VTest.app_port = 4010

        VTest.passwords = dict()
        VTest.usr = 'faxtest'
        VTest.pwd = '1.relav.!'

        #: The categories to be included are common across all tests
        VTest.cat_list = None

        #: The label to be included are common across all tests
        VTest.label = 'unknown run'

        #: The execution mode: None='normal', 'plan'.
        VTest.mode = None

        #: Do we need to export the output
        VTest.export = False

        #: The export file name.
        VTest.export_filename = None
        #: The export file instantiated upon execution of the test suite.
        VTest.export_file = None

        #: Indicating whether we are performing a queued parallel run
        VTest.parallel = False

        #: The list of test case instances which are to be run.
        VTest.tests = []

        #: The list of categories to be included in the run across all tests.
        VTest.categories = {}

        #: Flag indicating whether the test case header needs to be printed.
        VTest.need_to_print_header = None
        VTest.test_result_folder = 'test_result'

        VTest.label = 'full gates'
        VTest.cat_list = None
        VTest.mode = None
        VTest.export = False
        VTest.export_filename = None

        VTest.queue = None
        VTest.id_testrun = 0 # equal DB_test.id_testrun when a testrun is created in db for test.
        VTest.parallel_idx = 0

        VTest.procs = 0

        VTest.browser_name = "chrome"
        VTest.detail_report = None
        VTest.log_list = ['exception', 'assertion']
        VTest.func_and_cat_update = True

        VTest.test_folder = 'test_features'
        VTest.tests_for_this_run = 'define_tests.py'
        VTest.port_delta = 10

        VTest.sanity_test_step = 0

    @staticmethod
    def get_object_data(object_spec):
        """
        Retrieves an object from the backend.
        Parses the JSON and returns an instantiated object.
        @param object_spec: A string representing the object retrieval URL, e.g., "patients/val"
        @return: The JSON-parsed object.
        """
        assert isinstance(object_spec, str)
        conn = httplib.HTTPConnection(host=VTest.tapi_host, port=VTest.tapi_port)
        conn.request("GET", "/tapi/" + object_spec)
        response = conn.getresponse()
        json_str = response.read()
        result = None
        try:
            result = json.loads(json_str)
        except:
            VTest.log_assertion(VTest(), 'get_object_data returns no json data, object_spec: ' + object_spec, False)
        return result

    @staticmethod
    def reset_pwd(usr):
        '''
        Reset the password for the user specified.
        @param usr: string representing the login name.
        @return:    string representing the password.
        '''
        if VTest.parallel:
            raise Exception("Error: parallel running doesn't allow to change pwd.")

        letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        digits = ['0','1','2','3','4','5','6','7','8','9']
        # specials = ['~','`','!','@','#','$','%','^','&','*','(',')','_','-','+','=','|',']','[','{','}',':',';','"','<','>','.','?']

        # pattern for password in validate.js: alphaNumericSymbolRegex = /^[a-z0-9\.\!\@\#\$\%\^\&\*\-]+$/i
        # i.e. ['.','!','@','#','$','%','^','&','*','-'], but the '^' is illegal, we use the list below

        specials = ['!', '@', '#', '$', '%', '&', '*', '-', '.']

        pwd = ''
        for i in range(1,5):
            for j in range(1,3):
                pwd += random.choice(letters)
            for j in range(1,3):
                pwd += random.choice(digits)
            pwd += random.choice(specials)
        conn = psycopg2.connect(VTest.db_connection)
        cur = conn.cursor()
        cmd = "UPDATE vgroupvusers SET password = (crypt( '"+pwd+"', gen_salt('md5'))) where username='"+usr+"'; COMMIT; select 1"
        cur.execute(cmd)
        cur.close()
        conn.close()
        VTest.passwords[usr] = pwd
        return pwd

    @staticmethod
    def get_pwd(usr):
        """
        Retrieve the password for a user.
        If this is the first request, reset the password.
        @param usr: string representing the login name.
        @return:    string representing the password.
        """
        if not(usr in VTest.passwords):
            VTest.reset_pwd(usr)
        return VTest.passwords[usr]

    @staticmethod
    def add_test(test_to_add):
        """
        Add a single test case object instance
        @param test_to_add: object
        """
        VTest.tests.append(test_to_add)
        if VTest.func_and_cat_update:
            print 'Updating methods and categories for "' + test_to_add.__class__.__name__+'".'
            DB_test.function_and_category_update(test_to_add, VTest.categories)

    @staticmethod
    def add_tests(tests_to_add):
        """
        Add a list of test case object instances
        @param tests_to_add: list
        """
        for test in tests_to_add:
            VTest.tests.append(test)
        return

    @staticmethod
    def export_method(class_name, method_name, event_type=None, event_message=None):
        assertion_str = ', "' + event_type + '", "' + event_message + '"' if event_type is not None else ''
        # If the test method is associated with categories, then
        if VTest.cat_list is None:
            if method_name in VTest.categories:
                # Print one line per category.
                for cat in VTest.categories[method_name]:
                    VTest.export_file = open(VTest.export_filename, 'a')
                    VTest.export_file.write('"' + VTest.label + '", "' + VTest.git + '", "' + VTest.timestamp + '", "' + class_name + '", "' + method_name + '", "' + cat + '"' + assertion_str + '\n')
                    VTest.export_file.close()
            else:
                # Print a single line for this test method.
                VTest.export_file.write('"' + VTest.label + '", "' + VTest.git + '", "' + VTest.timestamp + '", ' + class_name + '", "' + method_name + '", ""' + assertion_str + '\n')
        elif method_name in VTest.categories:
            # Print one line per category.
            for cat in VTest.categories[method_name]:
                if cat in VTest.cat_list:
                    VTest.export_file = open(VTest.export_filename, 'a')
                    VTest.export_file.write('"' + VTest.label + '", "' + VTest.git + '", "' + VTest.timestamp + '", "' + class_name + '", "' + method_name + '", "' + cat + '"' + assertion_str + '\n')
                    VTest.export_file.close()
        else:
            # Print a single line for this test method.
            VTest.export_file = open(VTest.export_filename, 'a')
            VTest.export_file.write('"' + VTest.label + '", "' + VTest.git + '", "' + VTest.timestamp + '", ' + class_name + '", "' + method_name + '", ""' + assertion_str + '\n')
            VTest.export_file.close()

    @staticmethod
    def run_command(cmd):
        """
        Execute a shell command and return output as a list of lines
        @param cmd:  A string of the command to execute
        @return:
        """
        str = subprocess.check_output(cmd, shell=VTest.is_linux)
        return str[:len(str)-1]

    @staticmethod
    def current_relative_url():
        return VTest.browser.current_url[VTest.browser.current_url.index('#!/') + 2:999]

    @staticmethod
    def category(cat_name):
        """
        A decorator to define the categories associated with a test method.
        @param cat_name: The name of the category associated with the test method.
        @rtype : A wrapped category method.
        """
        # Define the decorator for this category invoked by Python to *decorate* the method.
        def cat_method(func):
            # Define the wrapper invoked whenever we want to execute the test method.
            def wrapper(*args):
                try:
                    # Before we can run the test method, we need to check if we should run it.
                    if VTest.should_test_method_run(VTest(), wrapper.method_name):
                        # We need to print the test case header when running the first method for this class
                        if VTest.need_to_print_header:
                            print
                            print '    testcase:"' + args[0].__class__.__name__ + '": '
                            if VTest.mode is None:
                                print
                            VTest.need_to_print_header = False
                        # When executing in parallel, we need to create files in the VTest.queue_in folder.
                        if VTest.parallel:
                            item_name = VTest.queue_in + '\\' + args[0].__class__.__name__ + '.' + wrapper.method_name;

                            if not(os.path.isfile(item_name)):
                                open(item_name, 'w').close()
                        # For normal execution mode
                        if VTest.mode is None:
                            # Execute the test once we know it is associated with a requested category.
                            func(*args)
                        # For plan mode, we only need to print the function mame; we don't need to execute
                        elif VTest.mode == 'plan':
                            print '        ' + wrapper.method_name
                        # For leaf (non-nested) functions, in 'normal' execution mode, we need to call done()
                        if func.__name__ != 'wrapper':
                            # For normal execution mode, after the test method completes
                            if VTest.mode is None:
                                # Tell the framework that the test completed.
                                # args[0] is self ...
                                args[0].done(wrapper.method_name)
                # Invoked from inside the wrapper method
                except:
                    #e = sys.exc_info()[0]
                    #print "Exception:", e
                    # Log the exception and continue with the next method.
                    args[0].log_exception(traceback.format_exc())
                    args[0].done(wrapper.method_name)

            # Once the wrapper function is defined, we need to associate it with the original (wrapped) method name.
            if func.__name__ == 'wrapper':
                # For nested wrappers, we copy the method name from the wrapper method.
                wrapper.method_name = func.method_name
            else:
                # For leaf wrappers, the name is the original methods name.
                wrapper.method_name = func.__name__
                # Next, we need to update the global category mappings.
            if not (wrapper.method_name in VTest.categories):
                # Initialize the key if it is not there yet.
                VTest.categories[wrapper.method_name] = []
                # ... and append the list of categories associated with this method.
            VTest.categories[wrapper.method_name].append(cat_name)
            # The decorator returns the wrapper method, which will be called instead of the test method.
            return wrapper

        # The decorator method to be invoked by Python for the decoration operation.
        return cat_method



class LogEntry:
    def __init__(self, event_type, event_message):
        """
        Represents a single entry in the log.
        This log is dumped only in case that the test case failed.
        @type self: LogEntry
        @param event_type: Event types are either 'failed','assertion','step','exception'
        @param event_message:
        @rtype : LogEntry
        """
        self.type = event_type
        self.message = event_message

