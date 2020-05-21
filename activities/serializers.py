from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, IntegerField, CharField

from activities.models import PreguntaOpcionMultiple, RespuestmultipleEstudiante, Opcionmultiple, Calificacion, Marca, \
    PreguntaFoV, Pausa, PreguntaAbierta, RespuestaAbiertaEstudiante, RespuestaVoF, Actividad

from interactive_content.models import ContenidoInteractivo
from .utils import get_total_qualifying_questions
from decimal import Decimal

class RespuestaSeleccionMultipleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestmultipleEstudiante
        fields = '__all__'

class QualificationMultipleChoiceResponseSerializer(RespuestaSeleccionMultipleSerializer):
    qualification = serializers.SerializerMethodField()

    def get_qualification(self, obj):
        total_qualifying_questions = get_total_qualifying_questions(obj.respuestmultiple.preguntaSeleccionMultiple.marca.contenido)
        qualification_by_question = 5/total_qualifying_questions if total_qualifying_questions > 0 else 0
        total_correct_options_by_question = Opcionmultiple.objects.filter(preguntaSeleccionMultiple=obj.respuestmultiple.preguntaSeleccionMultiple, esCorrecta=True).count()
        note_by_option = qualification_by_question/total_correct_options_by_question if total_correct_options_by_question > 0 else 0
        qualification, created = Calificacion.objects.get_or_create(
            estudiante=obj.estudiante, actividad=obj.respuestmultiple.preguntaSeleccionMultiple, defaults={"calificacion": 0}
        )
        note = note_by_option if obj.respuestmultiple.esCorrecta else -note_by_option
        note = note if created else qualification.calificacion + Decimal(note)
        qualification.calificacion = 0 if note < 0 else note
        qualification.save()
        return qualification.calificacion

class RespuestaAbiertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaAbiertaEstudiante
        fields = '__all__'

class RespuestaFoVSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaVoF
        fields = '__all__'

class QualificationFoVResponseSerializer(RespuestaFoVSerializer):
    qualification = serializers.SerializerMethodField()

    def get_qualification(self, obj):
        total_qualifying_questions = get_total_qualifying_questions(obj.preguntaVoF.marca.contenido)
        note = 5/total_qualifying_questions if total_qualifying_questions > 0 and obj.preguntaVoF.esVerdadero == obj.esVerdadero else 0
        qualification, _ = Calificacion.objects.update_or_create(
            estudiante=obj.estudiante, actividad=obj.preguntaVoF, defaults={"calificacion": note}
        )
        return qualification.calificacion

    class Meta:
        model = RespuestaVoF
        fields = '__all__'

class CalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = ('id', 'estudiante', 'actividad', 'calificacion')


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'


class OpcionmultipleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcionmultiple
        fields = '__all__'


class PreguntaOpcionMultipleSerializer(serializers.ModelSerializer):
    opciones = OpcionmultipleSerializer(read_only=True, many=True)

    class Meta:
        model = PreguntaOpcionMultiple
        fields = '__all__'


class PreguntaAbiertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaAbierta
        fields = '__all__'


class OpcionMultipleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcionmultiple
        fields = '__all__'


class PreguntaFoVSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaFoV
        fields = '__all__'


class PreguntaFoVModificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaFoV
        fields = ('pregunta', 'nombre', 'retroalimentacion', 'numeroDeIntentos', 'esVerdadero', 'tieneRetroalimentacion')


class PausaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pausa
        fields = '__all__'


class PreguntaAbiertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaAbierta
        fields = '__all__'

class MarcaConTipoActividadSerializer(serializers.ModelSerializer):
    marca_id = IntegerField(source="marca.id")
    nombre = CharField(source="marca.nombre")
    punto = IntegerField(source="marca.punto")
    contenido = IntegerField(source="marca.contenido_id")

    class Meta:
        model = Actividad
        fields = ["tipoActividad", "marca_id", "nombre", "punto", "contenido"]

class ActividadPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ["id", "retroalimentacion"]

class MarcaSerializerRetroalimentacion(serializers.ModelSerializer):
    actividades = serializers.SerializerMethodField('get_act')

    def get_act(self, marca):
        qs = Actividad.objects.filter(marca=marca)
        serializer = ActividadPreguntaSerializer(instance=qs, many=True)
        return serializer.data
    class Meta:
        model = Marca
        fields = ["id", "actividades"]

class ContenidoInteractivoRetroalimentacionSerializer(serializers.ModelSerializer):
    marcas = MarcaSerializerRetroalimentacion(read_only=True, many=True)

    class Meta:
        model = ContenidoInteractivo
        fields = fields = ["id", "marcas"]
