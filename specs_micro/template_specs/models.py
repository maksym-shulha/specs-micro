from django.db import models


class Producer(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)


class DisplaySize(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)


class Series(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)


class Cpu(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)


class Gpu(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)


class Category(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20)
