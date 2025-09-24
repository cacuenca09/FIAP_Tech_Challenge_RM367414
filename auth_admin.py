from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from auth import get_current_admin_user
from typing import Optional
import asyncio
from datetime import datetime

# Router para as rotas administrativas
admin_router = APIRouter(prefix="/api/v1", tags=["Administração"])

# Simulação de status de scraping
scraping_status = {
    "is_running": False,
    "last_run": None,
    "total_books_scraped": 0,
    "status": "idle"
}

async def simulate_scraping_task():
    """Simula uma tarefa de scraping em background"""
    global scraping_status
    
    scraping_status["is_running"] = True
    scraping_status["status"] = "running"
    scraping_status["last_run"] = datetime.now().isoformat()
    
    try:
        # Simula processo de scraping (5 segundos)
        for i in range(5):
            await asyncio.sleep(1)
            scraping_status["total_books_scraped"] += 10
        
        scraping_status["status"] = "completed"
        
    except Exception as e:
        scraping_status["status"] = f"error: {str(e)}"
    finally:
        scraping_status["is_running"] = False

@admin_router.post("/scraping/trigger")
def trigger_scraping(
    background_tasks: BackgroundTasks,
    force: bool = False,
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Dispara processo de scraping de livros (ADMIN ONLY)
    
    - **force**: Se True, força novo scraping mesmo se já estiver rodando
    
    **Requer:**
    - Token de acesso válido
    - Role de admin
    - Header: Authorization: Bearer <admin_token>
    
    **Funcionalidade:**
    - Inicia processo de scraping em background
    - Retorna status atual do processo
    - Apenas um processo de scraping pode rodar por vez (exceto se force=True)
    """
    global scraping_status
    
    # Verifica se já está rodando
    if scraping_status["is_running"] and not force:
        raise HTTPException(
            status_code=400,
            detail="Scraping já está em execução. Use force=true para forçar novo processo."
        )
    
    # Inicia tarefa em background
    background_tasks.add_task(simulate_scraping_task)
    
    return {
        "message": "Scraping iniciado com sucesso",
        "initiated_by": current_admin["username"],
        "initiated_at": datetime.now().isoformat(),
        "force_used": force,
        "status": scraping_status
    }

@admin_router.get("/scraping/status")
def get_scraping_status(current_admin: dict = Depends(get_current_admin_user)):
    """
    Verifica status atual do scraping (ADMIN ONLY)
    
    **Requer:**
    - Token de acesso válido
    - Role de admin
    - Header: Authorization: Bearer <admin_token>
    
    **Retorna:**
    - Status atual do processo
    - Última execução
    - Total de livros coletados
    - Se está rodando no momento
    """
    return {
        "current_status": scraping_status,
        "checked_by": current_admin["username"],
        "checked_at": datetime.now().isoformat()
    }

@admin_router.post("/scraping/stop")
def stop_scraping(current_admin: dict = Depends(get_current_admin_user)):
    """
    Para processo de scraping em execução (ADMIN ONLY)
    
    **Requer:**
    - Token de acesso válido
    - Role de admin
    - Header: Authorization: Bearer <admin_token>
    
    **Nota:** Esta é uma implementação simulada.
    Em produção, seria necessário um mecanismo real de cancelamento.
    """
    global scraping_status
    
    if not scraping_status["is_running"]:
        raise HTTPException(
            status_code=400,
            detail="Nenhum processo de scraping está em execução."
        )
    
    # Em uma implementação real, você cancelaria a tarefa aqui
    scraping_status["is_running"] = False
    scraping_status["status"] = "stopped"
    
    return {
        "message": "Scraping interrompido com sucesso",
        "stopped_by": current_admin["username"],
        "stopped_at": datetime.now().isoformat(),
        "status": scraping_status
    }

@admin_router.get("/admin/dashboard")
def admin_dashboard(current_admin: dict = Depends(get_current_admin_user)):
    """
    Dashboard administrativo com informações do sistema (ADMIN ONLY)
    
    **Requer:**
    - Token de acesso válido
    - Role de admin
    - Header: Authorization: Bearer <admin_token>
    """
    return {
        "message": "Bem-vindo ao dashboard administrativo",
        "admin_user": current_admin["username"],
        "system_info": {
            "scraping_status": scraping_status,
            "total_registered_users": 2,  # admin + user
            "api_status": "operational"
        },
        "available_actions": [
            "Trigger scraping",
            "View scraping status", 
            "Stop scraping",
            "Monitor system health"
        ]
    }