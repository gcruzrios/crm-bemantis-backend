import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    vendedor = "vendedor"
    visualizador = "visualizador"


class CompanySource(str, enum.Enum):
    referido = "referido"
    web = "web"
    evento = "evento"
    llamada = "llamada"
    redes_sociales = "redes_sociales"
    publicidad = "publicidad"
    otro = "otro"


class DealStage(str, enum.Enum):
    prospecto = "prospecto"
    calificado = "calificado"
    propuesta = "propuesta"
    negociacion = "negociacion"
    ganado = "ganado"
    perdido = "perdido"


class QuoteStatus(str, enum.Enum):
    borrador = "borrador"
    enviada = "enviada"
    aceptada = "aceptada"
    rechazada = "rechazada"
    expirada = "expirada"


class ActivityType(str, enum.Enum):
    llamada = "llamada"
    email = "email"
    reunion = "reunion"
    tarea = "tarea"
    nota = "nota"
