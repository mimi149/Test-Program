import os
from vtest import VTest
import sys
import json
import getopt
from db_test import DB_test

def create_necessary_folder():

    if VTest.id_testrun == 0:
        VTest.id_testrun = DB_test.testrun_update(VTest.git, VTest.timestamp, VTest.browser_name)
        VTest.test_result_folder = 'test_result-' + str(VTest.id_testrun)
        if not os.path.isdir(VTest.test_result_folder):
            os.mkdir(VTest.test_result_folder)

        VTest.selector_for_test_filename = "json/selector_for_test.json"
        VTest.selector_json = json.loads(open(VTest.selector_for_test_filename, 'r').read())

        VTest.test_value_filename = "json/test_value.json"
        VTest.test_value = json.loads(open(VTest.test_value_filename, 'r').read())

        VTest.updated_value_filename = VTest.test_result_folder + "/updated_value.json"

        with open(VTest.updated_value_filename, "w") as outfile:
            git = {"git": VTest.git + '.' + VTest.timestamp[:16]}
            json.dump(git, outfile, indent=4)

def main(argv):

    VTest.init()

    try:
        opts, args = getopt.getopt(argv, "hvl:c:u:t:px:q:j:b:rg:fo:d:",
                                   ["help", "version", "label=", "categories=", "user=", "tests=", "plan", "export=", "queue", "jprocs=", "browser=", "log=", "port=", "folder="])
    except getopt.GetoptError:
        print 'parameters required; use "rtest.py -h"'
        sys.exit(2)

    arg = ''
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            prefix = 'usage: python rtest.py '
            wrapper = textwrap.TextWrapper(initial_indent=prefix, width=80, subsequent_indent=' ' * len(prefix))
            helpstr = "--version   --label <label>   --categories <categories>   --user <user:password>   --tests <test_py_file>   --plan   --export <export_file_name>   --jprocs <#_of_processes>"
            print
            print wrapper.fill(helpstr)
            print
            print "option       short      description"
            print "------------ ---------- ----------------------------------------------------------------"
            print "--help       -h         Provide this help message."
            print "                        Tests are organized into classes and methods, representing "
            print "                        test cases, and test methods respectively."
            print "                        Classes must inherit from the \'VTest\' base class. For example:"
            print
            print "                        from vtest import *"
            print
            print "                        class testcase_find_create_patient(VTest):"
            print "                            ... "
            print
            print "                        Not all class methods are classified as test methods.  To be "
            print "                        classified as a test method its names must start with \'when_\'"
            print "                        and include \'_expect_\'.  For example, the following method "
            print "                        will be classified as a test method:"
            print
            print "                        def when_creating_a_patient_expect_to_find_it_in_dropdown(self):"
            print "                            ..."
            print
            print "                        The framework will automatically run all test methods it finds, loaded"
            print "                        from the file specified by the -t parameter and associated with the"
            print "                        categories specified by the -c parameter"
            print
            print "--version    -v         The version of the testing framework."
            print
            print "--label      -l         The gates label which this run represents; the 'full gates' label"
            print "                        will be used if this parameter is omitted.  This label will be"
            print "                        logged in the output messages and the exported records."
            print
            print "--categories -c         The categories to run; the default of running all categories is"
            print "                        applied if this parameter is omitted.  Multiple categories are"
            print "                        delimited using the \'+\' character.  For example, -c \"cat1+cat2\""
            print "                        specified running all tests which are associated either with"
            print "                        category cat1 or cat2.  To associate a method with a category cat1"
            print "                        use a category decorator in the function definition as follows:"
            print
            print "                        @VTest.category('cat1')"
            print "                        def when_creating_a_patient_expect_to_find_it_in_dropdown(self):"
            print "                            ...."
            print
            print "--port        -o        The port delta over 4000.  For example, when \'20\' is provided, then"
            print "                        TAPI port is 5020 and API port is 4020"
            print
            print "--user        -u        The username and password to be used when logging into the application."
            print "                        This enables the system to test specific roles and permissions associated"
            print "                        with specific users.  The user and password are separated by \':\'. "
            print "                        For example, use -u \"user1:password1\" to specify using \"user1\" as the"
            print "                        user, and \"password1\" as the password."
            print
            print "--tests       -t        The python file which loads the test.  Typically this file will import"
            print "                        classes and invoke their constructors.  For example, -t \"define_tests.py\" "
            print "                        will execute the code in \"define_tests.py\".  A typical code in that file"
            print "                        would import the test case class and add its instantiation to the tests:"
            print
            print "                        from testcase_menu_bar import *"
            print "                        VTest.add_test(testcase_menu_bar())"
            print
            print "--plan        -p        Print the lists of test which are to be executed by the settings provided,"
            print "                        instead of actually executing them.  This is useful to determine the scope"
            print "                        of the testing that will run without incuring the execution cost."
            print
            print "--export      -x        Export the output logs to a *.csv file, in addition to the console or stdout."
            print "                        This is very useful to enable usage of pivot tables to analyze test results."
            print
            print "--jprocs      -j        Specifies the number of concurrent processes to use; this implies an"
            print "                        asyncronous run:  The test framework will spawn the number specified of"
            print "                        console windows, and launch a queue-based test runner in each window."
            print "                        Each test runner will open the browser and run the tests in the queue."
            print "                        As a test is picked by for execution by one of the shell processes, it becomes"
            print "                        unavailable to the rest of the processes.  Processes continue to live for as long"
            print "                        as there are pending items in the queue.  The shell window closes once the last"
            print "                        test it picked up is complete.  For example, -j 4 will launch 4 independent test"
            print "                        processes."
            print "                        To determine the total number of tests in the queue, one can use the -p option,"
            print "                        or, alternatively, inspect the content of the queue_in directory."
            print
            print "--queue       -q        Specifies the name of the folder containing the functions to test"
            print "                        usage: '-q foldername', foldername cannot include character '-'."
            print "                        This arg is also used by the parallel running to call the subprocesses automatically."
            print
            print "--browser      -b       Specifies the name of the browser, use '-b Chrome' or '-b PhantomJS', Chrome browser"
            print "                        is default when missing -b"
            print
            print "--report       -r       The details of the test (the logs below) are saved in db_for_test only when "
            print "                        the test function is failed,"
            print "                        -r will save the details even when the test function is passed."
            print
            print "--log          -g       There are several kinds of actions needed to be logged:"
            print "                        'exception', 'assertion', 'login', 'find', 'type', 'selector'"
            print "                        The 'exception' and 'assertion' are logged by default, the others need "
            print "                        to follow this option. Multiple logs are delimited using the \'+\' character."
            print "                        For example, -g login+find+assertion"
            print
            print "--func         -f       -f will NOT update the methods and categories to the db for test. By default"
            print "                        they will be updated."
            print
            print "A number of built-in framework methods, defined in the base class VTest, which can be used within tests; "
            print "these methods are described below:"
            print
            print "goto_url:"
            print
            print "    The goto_url method enables jumping directly to a URL.  It is commonly used as the starting point"
            print "    of a test method.  As an example, one can go to the fax messages grid, or the patient details form,"
            print "    as the first step of testing the grid or form respectively.  The method usage is as follows:"
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    description       (Optional) The description of the location we are going to, e.g., \"Patients Details form\"."
            print "    relative_url      The location we are going to relative to the host and session of the URL. For example,"
            print "                      when going to \"http://192.168.102.128:4020/?v=g8989fae#!/patients/g/12/u/8/view/283\""
            print "                      we need to specify relative_url=\"/patients/g/12/u/8/view/283\""
            print
            print
            print "click_element:"
            print
            print "    This method perform simulated click on an element, and verifies the outcome."
            print "    It takes the common parameters of method, selector and description, as described below, plus a RegEx pattern"
            print "    used to match against the URL browsed to, when applicable.  If the pattern is None, then verification is skipped."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    method            The method by which the elemens is selected.  The following methods are currently supported:"
            print "                      When method=\"id\" then the element with the exact id is selected.  In case of multiple matches"
            print "                      only the first element is selected; it is critical to avoid multiple elements with the same id."
            print "                      When method=\"css\" then the content of the selector is interpreted as a full css selector."
            print "                      In case of multiple matches only the first is selected; it is critical to avoid multiple matches."
            print "                      When method=\"dialog-button\" then the dialog popup button with the name specified by the selector"
            print "                      is selected.  This method should only be used with popovers, because it relies on its pattern."
            print "    selector          The string specification of the selection filter.  The interpretation of the filter is controlled"
            print "                      by the value of the method parameter, as described above."
            print "    description       (Optional) The description of the element of which content is verified."
            print "    expected_browsed_url_pattern (Optional). When clicking on the element redirects the browser to a new URL, this"
            print "                      specifies a pattetn which is matched against the URL browsed to.  When the regex matches, the"
            print "                      assertion passes.  Otherwise, the assertion fails, and the logs provide both the URL and tne pattern/"
            print
            print
            print "assert_element_text:"
            print
            print "    This method verifies that the content of an element is as expected.  It can be used, e.g., to verify that the"
            print "    content of a grid cell is as expected, or that the detail view lists the correct fields and contains expected data,"
            print "    for example, the following field can be used to verify the presented of the \"First Name\" field in the "
            print "    expansion of \"PATIENT\" within the patient detail form:"
            print "    self.assert_element_text("
            print "      method='css', "
            print "      selector='div#selector-idinsured-details > div.ng-scope > div:nth-child(2) > div.selector-details-container-input > label.selector-details-label', "
            print "      expected_value = 'First', "
            print "      description = 'to confirm that \"First\" field is present at position #2' )"
            print
            print "      It is important to notice how deep the selector is, and the usage of \":nth-child(2)\" to pick out the specific"
            print "      field from a list of (sibling) fields.  This technique is critical to ensure a unique match of a single element."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    method            The method by which the elemens is selected.  The following methods are currently supported:"
            print "                      When method=\"id\" then the element with the exact id is selected.  In case of multiple matches"
            print "                      only the first element is selected; it is critical to avoid multiple elements with the same id."
            print "                      When method=\"css\" then the content of the selector is interpreted as a full css selector."
            print "                      In case of multiple matches only the first is selected; it is critical to avoid multiple matches."
            print "                      When method=\"dialog-button\" then the dialog popup button with the name specified by the selector"
            print "                      is selected.  This method should only be used with popovers, because it relies on its pattern."
            print "    selector          The string specification of the selection filter.  The interpretation of the filter is controlled"
            print "                      by the value of the method parameter, as described above."
            print "    expected_value    The expected text content of the selected elements.  If the content does not match, the"
            print "                      assertion fails and a log is triggerred.  The log will show the result of all other assertions"
            print "                      associated with this test method, including al those passing and failing."
            print "    description       (Optional) The description of the element of which content is verified."
            print
            print
            print "type_in_field:"
            print
            print "    This method enables typing text into form fields.  Selects the field and, subsequently, sends keystrokes to it."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    method            The method by which the elemens is selected.  The following methods are currently supported:"
            print "                      When method=\"id\" then the element with the exact id is selected.  In case of multiple matches"
            print "                      only the first element is selected; it is critical to avoid multiple elements with the same id."
            print "                      When method=\"css\" then the content of the selector is interpreted as a full css selector."
            print "                      In case of multiple matches only the first is selected; it is critical to avoid multiple matches."
            print "                      When method=\"dialog-button\" then the dialog popup button with the name specified by the selector"
            print "                      is selected.  This method should only be used with popovers, because it relies on its pattern."
            print "    selector          The string specification of the selection filter.  The interpretation of the filter is controlled"
            print "                      by the value of the method parameter, as described above."
            print "    text_to_type      The text which we are to type within a field."
            print "    description       (Optional) The description of the element of which content is verified."
            print
            print
            print "type_in_selector:"
            print
            print "    This method enables typing text filters into drodown filters, verifys the matches and enables selecting a specific match."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    method            The method by which the elemens is selected.  The following methods are currently supported:"
            print "                      When method=\"id\" then the element with the exact id is selected.  In case of multiple matches"
            print "                      only the first element is selected; it is critical to avoid multiple elements with the same id."
            print "                      When method=\"css\" then the content of the selector is interpreted as a full css selector."
            print "                      In case of multiple matches only the first is selected; it is critical to avoid multiple matches."
            print "                      When method=\"dialog-button\" then the dialog popup button with the name specified by the selector"
            print "                      is selected.  This method should only be used with popovers, because it relies on its pattern."
            print "    selector          The string specification of the selection filter.  The interpretation of the filter is controlled"
            print "                      by the value of the method parameter, as described above."
            print "    text_to_type      The text which we are to type within a field."
            print "    timeout           The text which we are to type within a field."
            print "    popover_id        (Optional; defaults to 'dropdown-overlay-popover')  Specifies the id of the dropdown overlay "
            print "                      container element; all dropdowns are implemented as singletons using a single container element"
            print "                      which is moved to the correct location.  This parameter is needed in case the dropdown is within"
            print "                      a popover, which would require creating a 2nd overlay container."
            print "    expected_match_count (Optional)  This field enables verifying the number of matches to the filter typed in the"
            print "                      selector.  If this parameter is ommitted, then the count verificaiton is skipped.  The logs"
            print "                      indicate whether the count verification matcvhed, failed or skipped."
            print "    item_index_to_select (Optional; defaults to selecting the 1st item)  This parameter enables selecting a specific"
            print "                      item from the list of matches.  If this value it provided, the item with the specified index"
            print "                      is selected.  Otherwise, no selection is performed."
            print "    expected_selection_pattern (Optional)  This is used to verify that the selection was performed for the correct item."
            print "                      When provided, the RegEx pattern is applied against the selected display key.  When not provided,"
            print "                      verification is skipped.  The logs indicate whether the selection matched the pattern, not matched,"
            print "                      or skipped."
            print "    description       (Optional) The description of the element of which content is verified."
            print
            print
            print "log_assertion:"
            print
            print "    This method is used to specify that an assertion was performed which does not involve any of the above methods."
            print "    The step will appear in the logs of the test method, only if at least one assertion failed for the test method."
            print "    Passing a value of passed=False will fail the assertion and force the logging to occur for the test method."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    message           This parameter specifies the message to be logged."
            print "    passed            When assigned to True the assertion passes; when assigned to False it failes."
            print "                      Logs will be forced when passed=False; otherwise, logs will not occur unless another assertion"
            print "                      failed."
            print
            print
            print "log_step:"
            print
            print "    This method is used to add a generic step logging for operations which do not involve any of the above methods."
            print "    The step will appear in the logs of the test method, only if at least one assertion failed for the test method."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    message           This parameter specifies the message to be logged."
            print
            print
            print "get_object_data:"
            print
            print "    This method is used to retrieve data from the backend TAPI.  It is useful to provide the test method access to the"
            print "    back-end data used to populate the front-end.  As an example, to test the create patient function, the this method"
            print "    was used to retrieve the list of all first and last names stored in the system, and generate a new unique name."
            print
            print "    parameter         description"
            print "    ----------------- ----------------------------------------------------------------"
            print "    object_spec       This parameter specifies the URL specificaiton of the object to be retrieved."
            print "                      As an example, use object_spec=\"patients/val\" to retrieve all patients in the system."
            print
            print

            sys.exit()

        elif opt in ("-v", "--version"):
            print 'vtest-1.0'
            sys.exit()
        elif opt in ("-l", "--label"):
            VTest.label = arg
        elif opt in ("-c", "--categories"):
            VTest.cat_list = arg.split('+')
        elif opt in ("-u", "--user"):
            s = arg.split(':')
            VTest.usr = s[0]
            VTest.pwd = s[1]
        elif opt in ("-t", "--tests"):
            tests_for_this_run = arg
        elif opt in ("-d", "--folder"):
            VTest.test_folder = arg
        elif opt in ('-o', "--port"):
            VTest.port_delta = arg
            VTest.app_port = int('40' + arg)
            VTest.tapi_port = int('50' + arg)
        elif opt in ('-p', "--plan"):
            VTest.mode = 'plan'
        elif opt in ('-x', "--export"):
            VTest.export = True
            VTest.export_filename = arg
        elif opt in ('-q', "--queue"):
            VTest.queue = True
            ids = arg.split('-')
            if len(ids) == 1: # This is not a subprocess of a parallel running, arg is the name of the folder containing the functions to test.
                VTest.queue_in = arg
                VTest.id_testrun = 0
                VTest.parallel_idx = 0
            else:
                VTest.id_testrun = int(ids[0])
                VTest.parallel_idx = int(ids[1])
                print 'queue VTest.id_testrun: ' + str(VTest.id_testrun) + ', VTest.parallel_idx: ' + str(VTest.parallel_idx)
        elif opt in ('-j', "--jprocs"):
            VTest.parallel = True
            VTest.procs = arg
        elif opt in ('-b', "--browser"):
            VTest.browser_name = arg
        elif opt in ('-r', "--report"):
            VTest.detail_report = True
        elif opt in ('-f', "--func"):
            VTest.func_and_cat_update = False
        elif opt in ("-g", "--log"):
            VTest.log_list.extend(arg.split('+'))

        VTest.base_url = 'http://' + VTest.app_host + ':' + str(VTest.app_port) + '/?v=' + VTest.git.split(':')[1] + '#!/'

        #: The login URL and credentials are common to all tests.
        VTest.login_url = VTest.base_url + 'login'

        # Process the conflict of some arguments:
        if VTest.parallel:
            for cat in ['pwd', 'pwd_symbol_test', 'time_out']:
                if cat in VTest.cat_list:
                    print "Parallel running doesn't test the category " + cat + " because it doesn't allow to change the password."
                    VTest.cat_list.remove(cat)

            if VTest.mode:
                print "Parallel running should not be phanned. The test starts to run now."
                VTest.mode = None

    create_necessary_folder()
    execfile(VTest.tests_for_this_run)

    if VTest.parallel or VTest.queue:
        if not os.path.isdir(VTest.queue_in):
            os.mkdir(VTest.queue_in)
        if not os.path.isdir(VTest.queue_out):
            os.mkdir(VTest.queue_out)
        if not os.path.isdir(VTest.not_test_now):
            os.mkdir(VTest.not_test_now)

    if VTest.queue:
        print 'VTest.cat_list: ', VTest.cat_list
        # This run_from_queue is not called from the parallel running and the id_testrun doesn't exist in db yet.
        if VTest.id_testrun == 0:
            VTest().run_from_queue(VTest.id_testrun, 0)

        # This run_from_queue is called from the parallel running and the id_testrun already exists in db.
        else:
            DB_test.id_testrun = VTest.id_testrun
            VTest().run_from_queue(VTest.id_testrun, VTest.parallel_idx)
    else:
        message_str = 'now running ' if VTest.mode is None else 'now planning '
        message_str += 'for categories ' + str(VTest.cat_list) + '.' if VTest.cat_list is not None else 'all categories.'
        print
        print 'Tests loaded from "' + VTest.tests_for_this_run + '"; ' + message_str
        if VTest.export:
            print 'Exporting all tests to ' + VTest.export_filename + '.'
        print

        VTest().run_all()

        if VTest.parallel:
            # Need to send to the subprocesses the parameters: -c -x, -b, -r, -g, -o

            VTest.log_list.remove('exception') # Prepare for sending to the subprocesses
            VTest.log_list.remove('assertion')
            c = ' -c ' + '+'.join(VTest.cat_list) if VTest.cat_list else ''
            b = ' -b ' + VTest.browser_name
            r = ' -r ' if VTest.detail_report else ''
            g = ' -g ' + '+'.join(VTest.log_list) if VTest.log_list else ''
            o = ' -o ' + str(VTest.port_delta)
            for parallel_idx in range(1, int(VTest.procs)+1):
                x = ' -x ' + 'test_parallel' + str(parallel_idx) + '.csv' if VTest.export else ''
                cmd = "start cmd /c python rtest.py -f" + " -q " + str(VTest.id_testrun)+'-'+str(parallel_idx) + c + x + b + r + g + o
                print 'cmd = ', cmd
                if VTest.mode is None:
                    os.system(cmd)


if __name__ == "__main__":
    main(sys.argv[1:])