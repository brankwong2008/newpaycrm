
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder
from django.shortcuts import render,redirect
from paycrm import settings
import os

class CurrencyHandler(PermissionHanlder,StarkHandler):
    page_title = "货币"

    # 新增一条记录
    def add_list(self, request, *args, **kwargs):
        page_title = self.page_title

        if request.method == "GET":
            form = self.get_model_form("add")()
            form = self.get_render_form(form, *args, **kwargs)
            namespace = self.namespace
            app_label = self.app_label
            popup_list = self.popup_list
            return render(request, self.add_list_template or "stark/change_list.html", locals())

        if request.method == "POST":
            form = self.get_model_form("add")(request.POST, request.FILES)

            if form.is_valid():
                result = self.save_form(form, request, False, *args, **kwargs)
                # 把新增的货币名字写入
                base_dir = settings.BASE_DIR
                file_path = os.path.join(base_dir, "paycrm/secret.py")
                try:
                    with open(file_path, "r") as f:
                        lines = f.readlines()

                    for idx, line in enumerate(lines):
                        if "DOLLAR_NAMES" in line:
                            print("target:", line)
                            # get all current currencies titles.
                            currency_objs = self.model_class.objects.all()
                            dollars_line = '['
                            for currency in currency_objs:
                                dollars_line+= '"%s",' % currency.title
                            dollars_line = "DOLLAR_NAMES=" + dollars_line + ']'
                            content = lines[:idx] + dollars_line.splitlines(True) + lines[idx + 1:]
                            print(content)
                            with open(file_path, "w") as f:
                                f.writelines(content)
                            break
                except Exception as e:
                    print("errors:", e)

                return result or redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, self.add_list_template or "stark/change_list.html", locals())



