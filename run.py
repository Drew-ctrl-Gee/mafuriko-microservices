"""MafurikoAI - Application Entry Point"""
from app import create_app, db
from app.models import User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


if __name__ == '__main__':
    print("=" * 60)
    print("   🌧️  MAFURIKO AI - Starting Server...")
    print("=" * 60)
    print("\n   🌐 Open: http://localhost:5000")
    print("   ⏹️  Stop: CTRL+C\n")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)