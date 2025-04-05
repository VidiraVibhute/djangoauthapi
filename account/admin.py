from unfold.admin import ModelAdmin
from django.contrib import admin
from account.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#from silk.models import Request, Response, Profile, SQLQuery

class UserModelAdmin(BaseUserAdmin):
  # The fields to be used in displaying the User model.
  # These override the definitions on the base UserModelAdmin
  # that reference specific fields on auth.User.
  list_display = ('id', 'email', 'name', 'tc', 'is_admin')
  list_filter = ('is_admin',)
  fieldsets = (
      ('User Credentials', {'fields': ('email', 'password')}),
      ('Personal info', {'fields': ('name', 'tc')}),
      ('Permissions', {'fields': ('is_admin',)}),
  )
  # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
  # overrides get_fieldsets to use this attribute when creating a user.
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email', 'name', 'tc', 'password1', 'password2'),
      }),
  )
  search_fields = ('email',)
  ordering = ('email', 'id')
  filter_horizontal = ()


# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)



# @admin.register(Request)
# class RequestAdmin(admin.ModelAdmin):
#     list_display = ("id", "path", "method", "start_time", "end_time")
#     search_fields = ("path", "method")
#     list_filter = ("method", "start_time")

# # @admin.register(Response)
# # class ResponseAdmin(admin.ModelAdmin):
# #     list_display = ("id", "status_code", "content_length", "request")
# #     search_fields = ("status_code",)
# #     list_filter = ("status_code",)

# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "time_taken")
#     search_fields = ("name",)
#     list_filter = ("time_taken",)

# @admin.register(SQLQuery)
# class SQLQueryAdmin(admin.ModelAdmin):
#     list_display = ("id", "query", "start_time", "end_time", "num_joins")
#     search_fields = ("query",)
#     list_filter = ("start_time",)

