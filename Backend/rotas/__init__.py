"""Blueprints do TPM. Cada arquivo agrupa as rotas de um assunto."""
from rotas.auth import bp as auth_bp
from rotas.alunos import bp as alunos_bp
from rotas.turmas import bp as turmas_bp
from rotas.fotos import bp as fotos_bp
from rotas.mensagens import bp as mensagens_bp

TODOS = (auth_bp, alunos_bp, turmas_bp, fotos_bp, mensagens_bp)
