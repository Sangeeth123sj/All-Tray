import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from requests import request

from tray.models import Institute, Store, Student


class StudentType(DjangoObjectType):
    class Meta:
        model = Student
        fields = "__all__"


class InstituteType(DjangoObjectType):
    class Meta:
        model = Institute
        fields = "__all__"


class StoreType(DjangoObjectType):
    class Meta:
        model = Store
        fields = "__all__"


class StudentNode(DjangoObjectType):
    class Meta:
        model = Student
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
        }
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="hi!")
    student = graphene.List(StudentType)
    student_by_name = graphene.Field(StudentType, name=graphene.String(required=True))
    college = graphene.List(InstituteType)
    store = graphene.List(StoreType)
    student_filter = relay.Node.Field(StudentNode)
    all_students = DjangoFilterConnectionField(StudentNode)

    def resolve_student(root, info):
        try:
            return Student.objects.all()
        except Student.DoesNotExist:
            return None

    def resolve_student_by_name(root, info, name):
        try:
            return Student.objects.get(name=name)
        except Student.DoesNotExist:
            return "no student found"

    def resolve_college(root, info):
        try:
            return Institute.objects.all()
        except Institute.DoesNotExist:
            return None

    def resolve_store(root, info):
        try:
            return Store.objects.all()
        except Store.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
