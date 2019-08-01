import logging
import time
import netmiko

# logging.basicConfig(
#     # filename="ios_conf_handler.log",
#     level=logging.DEBUG,
#     format="[%(levelname)s] %(asctime)s (%(threadName)-4s): %(message)s",
# )

default_password_list = []
with open("default_passwords.txt", "r") as passwords_file:
    for line in passwords_file:
        default_password_list.append(line.strip(" \n"))


class _Device:

    def __init__(self, name: str, address: str, port: int or str, user_password: str, priv_password: str):
        self.name = name
        self.priv_password = priv_password
        self.user_password = user_password
        self.address = address
        self.port = port
        self.conf_file_path = "device_list_and_configs/{}.txt".format(name)

    def _open_telnet_and_login_to_user_EXEC(self):
        logging.info('_open_telnet_and_login_to_user_EXEC: trying to open telnet connection')
        if self.user_password == "":
            for password in default_password_list:  # пробуем залогинится используя дефолтные пароли
                try:
                    logging.info('_open_telnet_and_login_to_user_EXEC: password:'+password)
                    self.telnet_netmiko = netmiko.Netmiko(host=self.address,
                                                          password=password,
                                                          secret='',
                                                          port=self.port,
                                                          device_type='cisco_ios_telnet',
                                                          timeout=20,
                                                          session_timeout=10,
                                                          auth_timeout=15)
                    self.user_password = password
                    break
                except netmiko.NetMikoAuthenticationException:
                    logging.info('_open_telnet_and_login_to_user_EXEC: pass try')
                    continue


            else:  # если произошел выход из цикла не изза "break", тоесть не удалось залогинится в девайс, то сообщаем об этом
                raise netmiko.NetMikoAuthenticationException("Login to user EXEC failed: {}".format(self.name))

        else:
            self.telnet_netmiko = netmiko.Netmiko(host=self.address,
                                                  password=self.user_password,
                                                  secret=self.priv_password,
                                                  port=self.port,
                                                  device_type='cisco_ios_telnet',
                                                  timeout=20,
                                                  session_timeout=10,
                                                  auth_timeout=15)

            # _init__(global_delay_factor=1, blocking_timeout=8, response_return=None, serial_settings=None, encoding=u'ascii')

        logging.info('_open_telnet_and_login_to_user_EXEC: opened telnet connection')

    def _close_telnet(self):
        self.telnet_netmiko.disconnect()
        logging.info('_close_telnet: closed telnet connection')

    def _login_to_priv_EXEC(self):

        if self.priv_password == "":
            for password in default_password_list:  # пробуем залогинится используя дефолтные пароли
                try:
                    self.telnet_netmiko.secret = password
                    self.telnet_netmiko.enable()
                    self.priv_password = password
                    break
                except ValueError:

                    logging.info('_login_to_priv_EXEC: pass try')
                    continue
                except netmiko.ssh_exception.NetMikoTimeoutException:
                    self.telnet_netmiko.send_command("\n", expect_string="({}|assword)".format(self.telnet_netmiko.base_prompt),
                                                     strip_command=False,
                                                     strip_prompt=False)


            else:  # если произошел выход из цикла не изза "break", тоесть не удалось залогинится в девайс, то сообщаем об этом
                raise netmiko.NetMikoAuthenticationException("Login to priv EXEC failed: {}".format(self.name))

            logging.info('_login_to_priv_EXEC: successful login to priv_EXEC')
            return
        else:
            self.telnet_netmiko.enable()
            logging.info('_________________________login_to_priv: successful login to priv_EXEC')
            return

    def _erase_startup_configuration(self):  # erase startup-config
        output = self.telnet_netmiko.send_command("erase startup-config", expect_string="confirm", strip_command=False, strip_prompt=False)
        logging.info(output)
        if "confirm" in output:
            output = self.telnet_netmiko.send_command("\n", strip_command=False, strip_prompt=False)
            logging.info(output)
            logging.info('_erase_startup_configuration: successful erase startup-config')
            time.sleep(1)
        else:
            logging.warning('_erase_startup_configuration: unsuccessful erase startup-config\n' + output)
            self._close_telnet()

    def _reload_devise(self):

        output = self.telnet_netmiko.send_command("reload", expect_string="(confirm|yes/no)",strip_command=False, strip_prompt=False)
        logging.info(output)

        if "Proceed with reload" in output:
            output = self.telnet_netmiko.send_command("\n", expect_string="Reload Reason", strip_command=False, strip_prompt=False)
            logging.info(output)
            logging.info("_reload_devise: successful")
        elif "System configuration has been modified" in output:  # System configuration has been modified. Save? [yes/no]:
            output = self.telnet_netmiko.send_command("no",expect_string="confirm", strip_command=False, strip_prompt=False)
            logging.info(output)
            if "Proceed with reload" in output:
                output = self.telnet_netmiko.send_command("\n", expect_string="Reload Reason", strip_command=False, strip_prompt=False)
                logging.info(output)
                logging.info("_reload_devise: successful")
            else:
                logging.warning("_reload_devise:| unsuccessful\n" + output)
                self._close_telnet()
        else:
            logging.warning("_reload_devise: unsuccessful\n" + output)
            self._close_telnet()

    def _update_configuration(self):
        configuration=[]
        with open(self.conf_file_path, "r") as f:
            for conf_line in f:
                configuration.append(conf_line.strip(" \n"))

        output = self.telnet_netmiko.send_config_set(configuration, strip_command=False, strip_prompt=False)

        logging.info("_update_conf: configuration entered")

    def _read_and_save_running_configuration_to_conf_file(self):
        conf_to_save = self.telnet_netmiko.send_command("show running-config", strip_command=True, strip_prompt=True)

            # output = output.lstrip(" \x08")
            # last_new_line_ch = output.rfind("\r\n")
            # conf_to_save += output[:last_new_line_ch + 1]


        logging.info("_read_and_save: successful read conf")
        # conf_to_save = conf_to_save.replace("\r\n", "\n")
        # conf_to_save = conf_to_save[conf_to_save.find("version"):]
        with open(self.conf_file_path, "w") as conf_file:
            conf_file.write(conf_to_save)

        logging.info("_read_and_save: successful save to file")

    def _save_configuration(self):
        output=self.telnet_netmiko.save_config(confirm=False) #confirm=False confirm_response=""

        logging.info(output)
        logging.info("_save_configuration: successful")


    def erase_configuration(self):
        self._open_telnet_and_login_to_user_EXEC()
        self._login_to_priv_EXEC()
        time.sleep(5)
        self._erase_startup_configuration()
        self._reload_devise()
        self._close_telnet()

    def update_configuration(self):
        self._open_telnet_and_login_to_user_EXEC()
        self._login_to_priv_EXEC()
        time.sleep(5)
        self._update_configuration()
        self._save_configuration()
        self._close_telnet()

    def write_configuration(self):
        self._open_telnet_and_login_to_user_EXEC()
        self._login_to_priv_EXEC()
        time.sleep(5)
        self._erase_startup_configuration()
        self._reload_devise()
        self._close_telnet()
        time.sleep(150)
        self._open_telnet_and_login_to_user_EXEC()
        self._login_to_priv_EXEC()
        time.sleep(5)
        self._update_configuration()
        self._save_configuration()
        self._close_telnet()

    def read_configuration(self):
        self._open_telnet_and_login_to_user_EXEC()
        self._login_to_priv_EXEC()
        time.sleep(5)
        self._read_and_save_running_configuration_to_conf_file()
        self._close_telnet()


def erase_configuration(name: str, address: str, port: int, user_password: str = "", priv_password: str = ""):
    d = _Device(name, address, port, user_password, priv_password)
    d.erase_configuration()


def update_configuration(name: str, address: str, port: int, user_password: str = "", priv_password: str = ""):
    d = _Device(name, address, port, user_password, priv_password)
    d.update_configuration()


def write_configuration(name: str, address: str, port: int, user_password: str = "", priv_password: str = ""):
    d = _Device(name, address, port, user_password, priv_password)
    d.write_configuration()


def read_configuration(name: str, address: str, port: int, user_password: str = "", priv_password: str = ""):
    d = _Device(name, address, port, user_password, priv_password)
    d.read_configuration()
