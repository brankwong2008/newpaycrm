from django.db import models

# Create your models here.

class Menu(models.Model):
    """一级菜单表"""
    sequence = models.SmallIntegerField(verbose_name='次序',default=0)
    title = models.CharField(max_length=30,verbose_name="一级菜单")
    icon = models.CharField(max_length=30,verbose_name="图标",null=True)
    def __str__(self):
        return self.title

class Permission(models.Model):
    """
    关系结构如下：
    一级菜单(订单管理)-
           |- 二级菜单（订单列表，订单统计），用menu与一级菜单Menu绑定
           |- 不能作为菜单的权限（订单增加，订单修改，订单删除），用pid与其二级菜单绑定
    """
    title = models.CharField(max_length=30,verbose_name="权限名")
    name = models.CharField(max_length=128,verbose_name="权限别名",null=True,unique=True)
    urls =  models.CharField(max_length=128,verbose_name="权限URL")
    icon = models.CharField(max_length=30, verbose_name="图标",null=True,blank=True)
    menu = models.ForeignKey(to='Menu',on_delete=models.CASCADE, null=True,blank=True, verbose_name="所属一级菜单", help_text="null表示不是菜单")
    parent = models.ForeignKey(to='Permission',on_delete=models.CASCADE, null=True,blank=True, verbose_name="父级菜单")

    def __str__(self):
        return self.title

class Role(models.Model):
    title = models.CharField(max_length=30,verbose_name="角色名")
    permissions = models.ManyToManyField(to="Permission",verbose_name="权限")
    def __str__(self):
        return self.title

class MyUser(models.Model):
    username = models.CharField(max_length=128, verbose_name="用户名")
    password = models.CharField(max_length=128, verbose_name="密码")
    email = models.CharField(max_length=128, verbose_name="邮箱",null=True,blank=True)
    roles = models.ManyToManyField(to=Role, verbose_name="角色",null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        abstract = True




