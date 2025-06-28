"""
compliance/enterprise_audit.py
Enhanced enterprise compliance and audit system for Watchtower.
Implements SIEM integration, regulatory compliance hooks, and comprehensive audit reporting.
"""

import json
import csv
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from database.models.events import Event
from database.models.ledger import LedgerEntry
from database.models.agents import Agent
from database.models.compliance import ComplianceRule, ComplianceViolation
from config.settings import settings

@dataclass
class AuditReport:
    """Represents a comprehensive audit report."""
    report_id: str
    report_type: str
    generated_at: datetime
    time_range: Dict[str, datetime]
    summary: Dict[str, Any]
    details: List[Dict[str, Any]]
    compliance_status: str
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any]

@dataclass
class ComplianceRule:
    """Represents a compliance rule for regulatory requirements."""
    rule_id: str
    name: str
    description: str
    regulatory_framework: str
    severity: str
    conditions: Dict[str, Any]
    actions: List[str]
    enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None

class EnterpriseAuditSystem:
    """Enterprise-grade audit and compliance system."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.siem_endpoints = settings.siem_endpoints or []
        self.compliance_rules = self._load_compliance_rules()
        self.regulatory_frameworks = {
            "SOX": "Sarbanes-Oxley Act",
            "GDPR": "General Data Protection Regulation",
            "HIPAA": "Health Insurance Portability and Accountability Act",
            "PCI-DSS": "Payment Card Industry Data Security Standard",
            "SOC2": "System and Organization Controls 2",
            "ISO27001": "ISO/IEC 27001 Information Security Management"
        }
    
    def generate_comprehensive_audit_report(self, 
                                          start_date: datetime,
                                          end_date: datetime,
                                          report_type: str = "comprehensive",
                                          include_violations: bool = True,
                                          include_recommendations: bool = True) -> AuditReport:
        """Generate a comprehensive audit report for the specified time range."""
        
        report_id = f"audit_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{report_type}"
        
        # Collect audit data
        events = self._get_events_in_range(start_date, end_date)
        ledger_entries = self._get_ledger_entries_in_range(start_date, end_date)
        violations = self._get_violations_in_range(start_date, end_date) if include_violations else []
        
        # Generate summary statistics
        summary = self._generate_summary_statistics(events, ledger_entries, violations)
        
        # Analyze compliance status
        compliance_status = self._analyze_compliance_status(violations, events)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(events, violations) if include_recommendations else []
        
        # Create detailed findings
        details = self._generate_detailed_findings(events, ledger_entries, violations)
        
        report = AuditReport(
            report_id=report_id,
            report_type=report_type,
            generated_at=datetime.utcnow(),
            time_range={"start": start_date, "end": end_date},
            summary=summary,
            details=details,
            compliance_status=compliance_status,
            violations=violations,
            recommendations=recommendations,
            metadata={
                "framework": "enterprise_audit",
                "version": "2.0",
                "generated_by": "watchtower_audit_system"
            }
        )
        
        # Ship to SIEM if configured
        self._ship_to_siem(report)
        
        return report
    
    def export_audit_report(self, report: AuditReport, format: str = "json") -> Union[str, bytes]:
        """Export audit report in specified format (JSON, CSV, PDF)."""
        
        if format.lower() == "json":
            return self._export_json(report)
        elif format.lower() == "csv":
            return self._export_csv(report)
        elif format.lower() == "pdf":
            return self._export_pdf(report)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def check_compliance_violations(self, events: List[Event]) -> List[Dict[str, Any]]:
        """Check events against compliance rules and identify violations."""
        
        violations = []
        
        for event in events:
            for rule in self.compliance_rules:
                if not rule.enabled:
                    continue
                
                if self._check_rule_conditions(event, rule.conditions):
                    violation = {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "regulatory_framework": rule.regulatory_framework,
                        "severity": rule.severity,
                        "event_id": event.id,
                        "event_type": event.event_type,
                        "timestamp": event.timestamp,
                        "description": f"Violation of {rule.name}: {rule.description}",
                        "details": {
                            "event_payload": event.payload,
                            "rule_conditions": rule.conditions
                        }
                    }
                    violations.append(violation)
                    
                    # Log violation to database
                    self._log_compliance_violation(violation)
        
        return violations
    
    def ship_to_siem(self, data: Dict[str, Any], siem_type: str = "splunk"):
        """Ship audit data to SIEM systems."""
        
        for endpoint in self.siem_endpoints:
            if endpoint.get("type") == siem_type:
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {endpoint.get('api_key', '')}"
                    }
                    
                    response = requests.post(
                        endpoint["url"],
                        json=data,
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code != 200:
                        print(f"Warning: SIEM shipment failed for {endpoint['url']}: {response.status_code}")
                        
                except Exception as e:
                    print(f"Error shipping to SIEM {endpoint['url']}: {str(e)}")
    
    def create_compliance_rule(self, rule_data: Dict[str, Any]) -> ComplianceRule:
        """Create a new compliance rule."""
        
        rule = ComplianceRule(
            rule_id=rule_data["rule_id"],
            name=rule_data["name"],
            description=rule_data["description"],
            regulatory_framework=rule_data["regulatory_framework"],
            severity=rule_data["severity"],
            conditions=rule_data["conditions"],
            actions=rule_data["actions"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        db_rule = ComplianceRule(
            rule_id=rule.rule_id,
            name=rule.name,
            description=rule.description,
            regulatory_framework=rule.regulatory_framework,
            severity=rule.severity,
            conditions=json.dumps(rule.conditions),
            actions=json.dumps(rule.actions),
            enabled=rule.enabled,
            created_at=rule.created_at,
            updated_at=rule.updated_at
        )
        
        self.db_session.add(db_rule)
        self.db_session.commit()
        
        # Reload compliance rules
        self.compliance_rules = self._load_compliance_rules()
        
        return rule
    
    def _load_compliance_rules(self) -> List[ComplianceRule]:
        """Load compliance rules from database."""
        
        db_rules = self.db_session.query(ComplianceRule).filter_by(enabled=True).all()
        rules = []
        
        for db_rule in db_rules:
            rule = ComplianceRule(
                rule_id=db_rule.rule_id,
                name=db_rule.name,
                description=db_rule.description,
                regulatory_framework=db_rule.regulatory_framework,
                severity=db_rule.severity,
                conditions=json.loads(db_rule.conditions),
                actions=json.loads(db_rule.actions),
                enabled=db_rule.enabled,
                created_at=db_rule.created_at,
                updated_at=db_rule.updated_at
            )
            rules.append(rule)
        
        return rules
    
    def _get_events_in_range(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """Get events within the specified time range."""
        
        return self.db_session.query(Event).filter(
            and_(
                Event.timestamp >= start_date,
                Event.timestamp <= end_date
            )
        ).order_by(desc(Event.timestamp)).all()
    
    def _get_ledger_entries_in_range(self, start_date: datetime, end_date: datetime) -> List[LedgerEntry]:
        """Get ledger entries within the specified time range."""
        
        return self.db_session.query(LedgerEntry).filter(
            and_(
                LedgerEntry.timestamp >= start_date,
                LedgerEntry.timestamp <= end_date
            )
        ).order_by(desc(LedgerEntry.timestamp)).all()
    
    def _get_violations_in_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get compliance violations within the specified time range."""
        
        db_violations = self.db_session.query(ComplianceViolation).filter(
            and_(
                ComplianceViolation.timestamp >= start_date,
                ComplianceViolation.timestamp <= end_date
            )
        ).order_by(desc(ComplianceViolation.timestamp)).all()
        
        violations = []
        for db_violation in db_violations:
            violation = {
                "rule_id": db_violation.rule_id,
                "rule_name": db_violation.rule_name,
                "regulatory_framework": db_violation.regulatory_framework,
                "severity": db_violation.severity,
                "event_id": db_violation.event_id,
                "timestamp": db_violation.timestamp,
                "description": db_violation.description,
                "details": json.loads(db_violation.details) if db_violation.details else {}
            }
            violations.append(violation)
        
        return violations
    
    def _generate_summary_statistics(self, events: List[Event], 
                                   ledger_entries: List[LedgerEntry],
                                   violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the audit report."""
        
        # Event statistics
        event_types = {}
        severity_counts = {"info": 0, "warning": 0, "error": 0, "critical": 0}
        
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
        
        # Violation statistics
        violation_by_framework = {}
        violation_by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for violation in violations:
            framework = violation["regulatory_framework"]
            violation_by_framework[framework] = violation_by_framework.get(framework, 0) + 1
            violation_by_severity[violation["severity"]] = violation_by_severity.get(violation["severity"], 0) + 1
        
        return {
            "total_events": len(events),
            "total_ledger_entries": len(ledger_entries),
            "total_violations": len(violations),
            "event_types": event_types,
            "severity_distribution": severity_counts,
            "violations_by_framework": violation_by_framework,
            "violations_by_severity": violation_by_severity,
            "compliance_score": self._calculate_compliance_score(violations)
        }
    
    def _analyze_compliance_status(self, violations: List[Dict[str, Any]], events: List[Event]) -> str:
        """Analyze overall compliance status."""
        
        critical_violations = [v for v in violations if v["severity"] == "critical"]
        high_violations = [v for v in violations if v["severity"] == "high"]
        
        if critical_violations:
            return "NON_COMPLIANT_CRITICAL"
        elif high_violations:
            return "NON_COMPLIANT_HIGH"
        elif violations:
            return "NON_COMPLIANT_LOW"
        else:
            return "COMPLIANT"
    
    def _generate_recommendations(self, events: List[Event], 
                                violations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on audit findings."""
        
        recommendations = []
        
        # Analyze violation patterns
        framework_violations = {}
        for violation in violations:
            framework = violation["regulatory_framework"]
            if framework not in framework_violations:
                framework_violations[framework] = []
            framework_violations[framework].append(violation)
        
        # Generate framework-specific recommendations
        for framework, violations_list in framework_violations.items():
            if len(violations_list) > 5:
                recommendations.append(
                    f"High number of {framework} violations detected. "
                    f"Review and update compliance controls for {framework} framework."
                )
        
        # Analyze event patterns
        error_events = [e for e in events if e.severity in ["error", "critical"]]
        if len(error_events) > 10:
            recommendations.append(
                "High number of error events detected. "
                "Review system health and implement additional monitoring."
            )
        
        return recommendations
    
    def _generate_detailed_findings(self, events: List[Event],
                                  ledger_entries: List[LedgerEntry],
                                  violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate detailed findings for the audit report."""
        
        findings = []
        
        # Add violation findings
        for violation in violations:
            findings.append({
                "type": "compliance_violation",
                "severity": violation["severity"],
                "timestamp": violation["timestamp"],
                "description": violation["description"],
                "details": violation["details"]
            })
        
        # Add critical events
        critical_events = [e for e in events if e.severity == "critical"]
        for event in critical_events:
            findings.append({
                "type": "critical_event",
                "severity": "critical",
                "timestamp": event.timestamp,
                "description": f"Critical event: {event.event_type}",
                "details": event.payload
            })
        
        return findings
    
    def _calculate_compliance_score(self, violations: List[Dict[str, Any]]) -> float:
        """Calculate compliance score based on violations."""
        
        if not violations:
            return 100.0
        
        severity_weights = {"low": 1, "medium": 3, "high": 7, "critical": 15}
        total_weight = sum(severity_weights[v["severity"]] for v in violations)
        
        # Score decreases with violations (max 100, min 0)
        score = max(0, 100 - (total_weight * 2))
        return round(score, 2)
    
    def _check_rule_conditions(self, event: Event, conditions: Dict[str, Any]) -> bool:
        """Check if an event matches compliance rule conditions."""
        
        for condition_key, condition_value in conditions.items():
            if condition_key == "event_type" and event.event_type != condition_value:
                return False
            elif condition_key == "severity" and event.severity != condition_value:
                return False
            elif condition_key == "payload_contains":
                if not isinstance(event.payload, dict):
                    return False
                if not any(condition_value in str(v) for v in event.payload.values()):
                    return False
        
        return True
    
    def _log_compliance_violation(self, violation: Dict[str, Any]):
        """Log compliance violation to database."""
        
        db_violation = ComplianceViolation(
            rule_id=violation["rule_id"],
            rule_name=violation["rule_name"],
            regulatory_framework=violation["regulatory_framework"],
            severity=violation["severity"],
            event_id=violation["event_id"],
            timestamp=violation["timestamp"],
            description=violation["description"],
            details=json.dumps(violation["details"])
        )
        
        self.db_session.add(db_violation)
        self.db_session.commit()
    
    def _ship_to_siem(self, report: AuditReport):
        """Ship audit report to SIEM systems."""
        
        siem_data = {
            "report_id": report.report_id,
            "report_type": report.report_type,
            "generated_at": report.generated_at.isoformat(),
            "compliance_status": report.compliance_status,
            "summary": report.summary,
            "violation_count": len(report.violations),
            "source": "watchtower_audit_system"
        }
        
        self.ship_to_siem(siem_data)
    
    def _export_json(self, report: AuditReport) -> str:
        """Export report as JSON."""
        return json.dumps(asdict(report), default=str, indent=2)
    
    def _export_csv(self, report: AuditReport) -> str:
        """Export report as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Report ID", "Type", "Generated At", "Compliance Status"])
        writer.writerow([report.report_id, report.report_type, report.generated_at, report.compliance_status])
        writer.writerow([])
        
        # Write summary
        writer.writerow(["Summary"])
        for key, value in report.summary.items():
            writer.writerow([key, value])
        writer.writerow([])
        
        # Write violations
        if report.violations:
            writer.writerow(["Violations"])
            writer.writerow(["Rule", "Framework", "Severity", "Timestamp", "Description"])
            for violation in report.violations:
                writer.writerow([
                    violation["rule_name"],
                    violation["regulatory_framework"],
                    violation["severity"],
                    violation["timestamp"],
                    violation["description"]
                ])
        
        return output.getvalue()
    
    def _export_pdf(self, report: AuditReport) -> bytes:
        """Export report as PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        story.append(Paragraph(f"Watchtower Audit Report: {report.report_id}", title_style))
        story.append(Spacer(1, 12))
        
        # Summary table
        summary_data = [["Metric", "Value"]]
        for key, value in report.summary.items():
            summary_data.append([key, str(value)])
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Summary", styles['Heading2']))
        story.append(summary_table)
        story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue() 