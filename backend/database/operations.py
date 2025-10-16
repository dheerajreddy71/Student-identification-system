"""
Database operations and CRUD functions
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from backend.database.models import Student, IdentificationLog, SystemMetrics, User
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib


class StudentDB:
    """Student database operations"""
    
    @staticmethod
    def create_student(db: Session, student_data: Dict[str, Any]) -> Student:
        """Create a new student record"""
        student = Student(**student_data)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    
    @staticmethod
    def get_student_by_id(db: Session, student_id: str) -> Optional[Student]:
        """Get student by student_id"""
        return db.query(Student).filter(Student.student_id == student_id).first()
    
    @staticmethod
    def get_student_by_roll(db: Session, roll_number: str) -> Optional[Student]:
        """Get student by roll number"""
        return db.query(Student).filter(Student.roll_number == roll_number).first()
    
    @staticmethod
    def get_student_by_faiss_index(db: Session, faiss_index: int) -> Optional[Student]:
        """Get student by FAISS index"""
        return db.query(Student).filter(Student.faiss_index == faiss_index).first()
    
    @staticmethod
    def get_all_students(db: Session, skip: int = 0, limit: int = 100, 
                        active_only: bool = True) -> List[Student]:
        """Get all students with pagination"""
        query = db.query(Student)
        if active_only:
            query = query.filter(Student.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search_students(db: Session, search_term: str) -> List[Student]:
        """Search students by name, student_id, or roll_number"""
        search = f"%{search_term}%"
        return db.query(Student).filter(
            or_(
                Student.name.ilike(search),
                Student.student_id.ilike(search),
                Student.roll_number.ilike(search),
                Student.department.ilike(search)
            )
        ).all()
    
    @staticmethod
    def update_student(db: Session, student_id: str, update_data: Dict[str, Any]) -> Optional[Student]:
        """Update student information"""
        student = StudentDB.get_student_by_id(db, student_id)
        if student:
            for key, value in update_data.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            student.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(student)
        return student
    
    @staticmethod
    def delete_student(db: Session, student_id: str) -> bool:
        """Soft delete student (set is_active to False)"""
        student = StudentDB.get_student_by_id(db, student_id)
        if student:
            student.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_next_faiss_index(db: Session) -> int:
        """Get next available FAISS index"""
        max_index = db.query(Student.faiss_index).order_by(desc(Student.faiss_index)).first()
        return (max_index[0] + 1) if max_index and max_index[0] is not None else 0
    
    @staticmethod
    def count_students(db: Session, active_only: bool = True) -> int:
        """Count total students"""
        query = db.query(Student)
        if active_only:
            query = query.filter(Student.is_active == True)
        return query.count()


class IdentificationLogDB:
    """Identification log database operations"""
    
    @staticmethod
    def create_log(db: Session, log_data: Dict[str, Any]) -> IdentificationLog:
        """Create identification log entry"""
        log = IdentificationLog(**log_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_recent_logs(db: Session, limit: int = 100) -> List[IdentificationLog]:
        """Get recent identification attempts"""
        return db.query(IdentificationLog).order_by(
            desc(IdentificationLog.timestamp)
        ).limit(limit).all()
    
    @staticmethod
    def get_logs_by_student(db: Session, student_id: str, limit: int = 50) -> List[IdentificationLog]:
        """Get logs for specific student"""
        return db.query(IdentificationLog).filter(
            IdentificationLog.student_id == student_id
        ).order_by(desc(IdentificationLog.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_success_rate(db: Session, hours: int = 24) -> float:
        """Calculate identification success rate"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        total = db.query(IdentificationLog).filter(
            IdentificationLog.timestamp >= cutoff
        ).count()
        
        if total == 0:
            return 0.0
        
        successful = db.query(IdentificationLog).filter(
            and_(
                IdentificationLog.timestamp >= cutoff,
                IdentificationLog.success == True
            )
        ).count()
        
        return (successful / total) * 100
    
    @staticmethod
    def get_average_latency(db: Session, hours: int = 24) -> Dict[str, float]:
        """Get average processing times"""
        from sqlalchemy import func
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        result = db.query(
            func.avg(IdentificationLog.preprocessing_time).label('avg_preprocessing'),
            func.avg(IdentificationLog.embedding_time).label('avg_embedding'),
            func.avg(IdentificationLog.search_time).label('avg_search'),
            func.avg(IdentificationLog.total_time).label('avg_total')
        ).filter(IdentificationLog.timestamp >= cutoff).first()
        
        return {
            'preprocessing': result.avg_preprocessing or 0.0,
            'embedding': result.avg_embedding or 0.0,
            'search': result.avg_search or 0.0,
            'total': result.avg_total or 0.0
        }


class SystemMetricsDB:
    """System metrics database operations"""
    
    @staticmethod
    def record_metric(db: Session, metric_type: str, metric_value: float, 
                     metric_unit: str, metadata: Dict = None):
        """Record a system metric"""
        metric = SystemMetrics(
            metric_type=metric_type,
            metric_value=metric_value,
            metric_unit=metric_unit,
            metadata=metadata or {}
        )
        db.add(metric)
        db.commit()
    
    @staticmethod
    def get_metrics(db: Session, metric_type: str, hours: int = 24) -> List[SystemMetrics]:
        """Get metrics of specific type"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return db.query(SystemMetrics).filter(
            and_(
                SystemMetrics.metric_type == metric_type,
                SystemMetrics.timestamp >= cutoff
            )
        ).order_by(SystemMetrics.timestamp).all()


class UserDB:
    """User database operations for authentication"""
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, hashed_password: str, 
                   full_name: str = None, role: str = "user") -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def update_last_login(db: Session, username: str):
        """Update user's last login timestamp"""
        user = UserDB.get_user_by_username(db, username)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
