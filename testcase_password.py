from vtest import *
import psycopg2

class testcase_password(VTest):

    def __init__(self):
        self.test_usr = 'jcrain'
        self.short_pwd = '123aB'
        self.long_pwd = '1234567890123456789aB'
        self.weak_pwd = '12345abc'
        self.wrong_pwd = 'wrong_password'
        self.legal_pwd1 = 'a!1234C@'
        self.legal_pwd2 = 'a!1234C@123'
        self.legal_pwd = 'aB123456'

        self.legal_symbols = ['!','@','#','$','%','&','*','-','.']
        self.symbols = ['~','`','!','@','#','$','%','^','&','*','(',')','_','-','+','=','|',']','[','{','}',':',';','"','<','>','.','?']

        # found illegal_symbols: ['~', '`', '^', '(', ')', '_', '+', '=', '|', ']', '[', '{', '}', ':', ';', '"', '<', '>', '?']
        # found legal symbols: ['!','@','#','$','%','&','*','-','.']

        # When running a test method, the fail flag will be initialized to False, and change to True when a failure assertion is detected.
        self.fail = None
        self.log = []

    def helper_user_permittance_reset(self):
        conn = psycopg2.connect(VTest.db_connection)
        cur = conn.cursor()
        cmd = "UPDATE vgroupvusers SET loginfailures = 0 where username='"+self.test_usr+"';"
        cur.execute(cmd)
        cmd = "UPDATE vgroupvusers SET islockedout = 0 where username='"+self.test_usr+"'; COMMIT; select 1;"
        cur.execute(cmd)
        cur.close()
        conn.close()

    def helper_change_password(self, current_pwd, new_pwd1, new_pwd2):
        param = {"method": 'css', "selector": 'input#password0', "text_to_type": current_pwd, "description": 'login with the current password'}
        self.type_in_field(**param)
        param = {"method": 'css', "selector": 'input#password1', "text_to_type": new_pwd1, "description": 'new legal password 1st time'}
        self.type_in_field(**param)
        param = {"method": 'css', "selector": 'input#password2', "text_to_type": new_pwd2, "description": 'new legal password 2nd time'}
        self.type_in_field(**param)

        param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
        param["selector"] = 'div.ui-dialog-buttonset > button:nth-child(2) > span'
        self.click_element(**param)

    def helper_login_and_go_to_password_changing_editor(self, usr, pwd, desc):
        # Remove the existent password when the parameter pwd is not required
        if not pwd:
            VTest.passwords.pop(usr, None)
        if not self.login_user(usr, pwd, desc, exception_raise=False):
            self.helper_user_permittance_reset()
            self.login_user(usr, pwd, desc)
        param = {"method": 'css', "selector": 'body > div.topbar > div.top-menu', "caller": 'helper_login_and_go_to_password_changing_editor'}
        # if 'login' in VTest.log_list:
        #     self.log_for_element(**param)
        param = {"method": "css", "description": None, "expected_browsed_url_pattern": None}
        param["selector"] = 'body > div.topbar > div.top-menu'
        self.click_element(**param)
        param["selector"] = 'a[ng-click="changePassword()"]'
        self.click_element(**param)

    @VTest.category('pwd')
    def when_logging_using_wrong_password_expect_server_side_error(self):
        # First-time logging will have an automated-setting password
        VTest.passwords.pop(self.test_usr, None)
        if not self.login_user(self.test_usr, pwd=None, description="to get an automated-setting password.", exception_raise=False):
            self.helper_user_permittance_reset()
            self.login_user(self.test_usr, pwd=None, description="to get an automated-setting password.")

        pwd = VTest.passwords.get(self.test_usr, '')

        self.log_step('Trying to login with a wrong password.')
        if self.login_user(self.test_usr, self.wrong_pwd, description="with a wrong password", exception_raise=False):
            self.log_assertion('User can login with a wrong password.', False)

    @VTest.category('pwd')
    def when_changing_to_legal_password_expect_successful_changing(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        pwd = VTest.passwords.get(self.test_usr, '')
        self.log_step('Trying to change password into a legal password')
        self.helper_change_password(pwd, self.legal_pwd1, self.legal_pwd1)

        self.assert_element_text('css', 'div.toast-message', expected_value='Successful')

    @VTest.category('pwd')
    def when_changing_to_legal_password_expect_successful_logging_using_new_password(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        pwd = VTest.passwords.get(self.test_usr, '')
        self.log_step('Trying to change password into a legal password')
        self.helper_change_password(pwd, self.legal_pwd1, self.legal_pwd1)

        self.assert_element_text('css', 'div.toast-message', expected_value='Successful')

        self.log_step('Trying to login with the new password.')
        if not self.login_user(self.test_usr, pwd=self.legal_pwd1, description="with the new password", exception_raise=False):
            self.helper_user_permittance_reset()
            if not self.login_user(self.test_usr, pwd=self.legal_pwd1, description="with the new password", exception_raise=False):
                self.log_assertion('User cannot login with a new password.', False)

    @VTest.category('pwd')
    def when_changing_password_using_wrong_current_password_expect_server_side_error(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        self.log_step('Trying to change password using a wrong current password.')
        self.helper_change_password('not_current_pwd', self.legal_pwd1, self.legal_pwd1)

        self.assert_element_text('css', 'div.toast-message',
                                 expected_value='The current password is not correct.')

    @VTest.category('pwd')
    def when_changing_to_short_password_expect_client_side_error(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        self.log_step('Trying to change password to a short password.')
        pwd = VTest.passwords.get(self.test_usr, '')
        self.helper_change_password(pwd, self.short_pwd, self.short_pwd)

        self.assert_element_text('css', 'small.error[ng-bind="form.errors.password1"]',
                                 expected_value='Field must be at least 8 characters in length.')

    @VTest.category('pwd')
    def when_changing_to_too_long_password_expect_server_side_error(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        self.log_step('Trying to change password to a too long password.')
        pwd = VTest.passwords.get(self.test_usr, '')
        self.helper_change_password(pwd, self.long_pwd, self.long_pwd)

        self.assert_element_text('css', 'div.toast-message',
                                 expected_value='Invalid password, 20 character maximum. See User Manual for password formats')

    @VTest.category('pwd')
    def when_changing_to_weak_password_expect_server_side_error(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        pwd = VTest.passwords.get(self.test_usr, '')
        self.log_step('Trying to change password to a weak password.')
        self.helper_change_password(pwd, self.weak_pwd, self.weak_pwd)

        self.assert_element_text('css', 'div.toast-message',
                                 expected_value='Password not strong enough. See User Manual for password formats')

    @VTest.category('pwd')
    def when_changing_password_with_not_matched_passwords_expect_client_side_error(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        pwd = VTest.passwords.get(self.test_usr, '')
        self.log_step('Trying to change pwd with the two not matched passwords.')
        self.helper_change_password(pwd, self.legal_pwd1, self.legal_pwd2)

        self.assert_element_text('css', 'small.error[ng-bind="form.errors.password2"]',
                                 expected_value='Field does not match the password1 field.')

    @VTest.category('pwd')
    def when_changing_to_the_same_current_password_expect_client_side_error(self):
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        self.log_step('Trying to change password to the same current password.')
        pwd = VTest.passwords.get(self.test_usr, '')
        self.helper_change_password(pwd, pwd, pwd)

        self.assert_element_text('css', 'small.error[ng-bind="form.errors.password1"]',
                                 expected_value='Field can not be the same as password0 field.')

    @VTest.category('pwd')
    def when_changing_password_and_changing_back_to_old_password_expect_successful_logging_using_old_password(self):
        VTest.passwords = {}
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

        pwd = VTest.passwords.get(self.test_usr, '')
        self.log_step('Change to some password.')
        self.helper_change_password(pwd, self.legal_pwd1, self.legal_pwd1)

        self.assert_element_text('css', 'div.toast-message', expected_value='Successful')

        self.log_step('Change back to the old password')
        self.helper_login_and_go_to_password_changing_editor(self.test_usr, self.legal_pwd1, "with the new password.")
        self.helper_change_password(self.legal_pwd1, pwd, pwd)

        self.assert_element_text('css', 'div.toast-message', expected_value='Successful')

        self.log_step('Trying to logging with the restored password')
        if not self.login_user(self.test_usr, self.legal_pwd1, description="with the new password", exception_raise=False):
            self.helper_user_permittance_reset()
            if not self.login_user(self.test_usr, pwd, description="with the restored password", exception_raise=False):
                self.log_assertion('User cannot login with the restored password.', False)

    @VTest.category('pwd_symbol_test')
    def when_changing_password_with_symbols_expect_finding_illegal_symbol_list(self):
        illegal_symbols = []
        legal_symbols = []
        for symbol in self.symbols:
            self.helper_login_and_go_to_password_changing_editor(self.test_usr, None, "to get an automated-setting password.")

            self.log_step('Trying to change to a password including some symbol.')
            pwd = VTest.passwords.get(self.test_usr, '')
            new_pwd = self.legal_pwd+symbol
            self.helper_change_password(pwd, new_pwd, new_pwd)

            self.log_step('Trying to login with the new password.')
            if not self.login_user(self.test_usr, pwd=new_pwd, description="with the new password", exception_raise=False):
                self.helper_user_permittance_reset()
                if not self.login_user(self.test_usr, pwd=new_pwd, description="with the new password", exception_raise=False):
                    illegal_symbols.append(symbol)
                else:
                    legal_symbols.append(symbol)
            else:
                legal_symbols.append(symbol)

        # Force to show the two lists of legal and illegal symbols
        if len(illegal_symbols) + len(legal_symbols) > 0:
            self.log_step('legal symbols: ' + ','.join(legal_symbols))
            self.log_step('Illegal symbols: ' + ','.join(illegal_symbols))
            self.login_user(self.test_usr, pwd="wrong_pwd", description="with the wrong password")

        # Result from this function:
        #     step: legal symbols: !,@,#,$,%,&,*,-,.
        #     step: Illegal symbols: ~,`,^,(,),_,+,=,|,],[,{,},:,;,",<,>,?

    @VTest.category('time_out')
    def when_waiting_15_min_expect_auto_log_out(self):
        VTest.passwords.pop(self.test_usr, None)
        if not self.login_user(self.test_usr, pwd=None, description="to get an automated-setting password.", exception_raise=False):
            self.helper_user_permittance_reset()
            self.login_user(self.test_usr, pwd=None, description="to get an automated-setting password.")
        logout_minutes = 15
        time.sleep(logout_minutes*60)
        if not('login' in VTest.browser.current_url):
            raise Exception('password', 'did not auto-log-out', 'after '+str(logout_minutes)+' minutes')


VTest.add_test(testcase_password())