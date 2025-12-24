"""
Modelo de Gasto para registro de egresos del consultorio.

Permite a la dueña llevar control de:
- Materiales e insumos odontológicos
- Matrículas y cursos
- Gastos operativos
- Otros gastos del negocio
"""

from datetime import datetime
from app.database import db


class Gasto(db.Model):
    """Modelo de gastos del consultorio."""
    
    __tablename__ = 'gastos'
    
    # Campos básicos
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    
    # Categorización
    categoria = db.Column(db.String(50), nullable=False)  # MATERIAL, INSUMO, MATRICULA, CURSO, OPERATIVO, OTRO
    
    # Detalles adicionales
    observaciones = db.Column(db.Text, nullable=True)
    comprobante = db.Column(db.String(100), nullable=True)  # Número de factura/recibo
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    creado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relaciones
    creado_por = db.relationship('Usuario', backref='gastos_registrados')
    
    def __repr__(self):
        return f'<Gasto {self.id}: {self.descripcion} - ${self.monto}>'
    
    @property
    def categoria_display(self):
        """Retorna el nombre legible de la categoría."""
        categorias = {
            'MATERIAL': 'Material Odontológico',
            'INSUMO': 'Insumos',
            'MATRICULA': 'Matrícula Profesional',
            'CURSO': 'Curso/Capacitación',
            'OPERATIVO': 'Gasto Operativo',
            'OTRO': 'Otro'
        }
        return categorias.get(self.categoria, self.categoria)
