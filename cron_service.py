#!/usr/bin/env python3
"""
Railway-compatible cron service for Polymarket Newsletter
Runs the newsletter generation every Friday at 6 PM PST
"""

import os
import time
import schedule
import logging
from datetime import datetime
from market_analyzer.newsletter_generator import MarketNewsletterGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/newsletter.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    required_vars = ['OPENAI_API_KEY', 'POSTMARK_API_KEY', 'TO_EMAILS']
    
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"❌ Missing required environment variable: {var}")
            return False
    
    logger.info("✅ All required environment variables are set")
    return True

def send_newsletter():
    """Generate and send the weekly newsletter"""
    try:
        logger.info("🚀 Starting weekly newsletter generation...")
        
        # Create newsletter generator with weekly parameters
        generator = MarketNewsletterGenerator(
            min_volume=10000,      # Default volume threshold
            min_change_pct=3.0,    # Default change threshold  
            max_markets=10000,     # Allow all markets
            hours_back=168,        # 7 days (168 hours)
            format_type="macro-outlook"
        )
        
        # Generate and email newsletter
        results = generator.generate_and_email_newsletter()
        
        if results["email_results"]["successful_sends"] > 0:
            logger.info(f"✅ Newsletter sent successfully to {results['email_results']['successful_sends']} recipients")
        else:
            logger.error(f"❌ Newsletter failed to send to all recipients")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Newsletter generation failed: {str(e)}")
        return False

def send_test_email():
    """Send a test email to verify configuration"""
    try:
        logger.info("🧪 Sending startup test email...")
        
        generator = MarketNewsletterGenerator()
        results = generator.send_test_email("Polymarket Newsletter Service - Weekly Job Active")
        
        if results["successful_sends"] > 0:
            logger.info("✅ Test email sent successfully")
            return True
        else:
            logger.error("❌ Test email failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test email failed: {str(e)}")
        return False

def main():
    """Main cron service loop"""
    logger.info("🌟 Starting Polymarket Newsletter Cron Service")
    
    # Validate environment
    if not validate_environment():
        logger.error("❌ Environment validation failed - exiting")
        exit(1)
    
    # Skip startup test email - service is ready
    
    # Schedule the newsletter for every Friday at 6 PM PST
    schedule.every().friday.at("18:00").do(send_newsletter)
    
    logger.info("⏰ Newsletter scheduled for every Friday at 6:00 PM PST")
    logger.info("🔄 Cron service running... (press Ctrl+C to stop)")
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Cron service stopped by user")
    except Exception as e:
        logger.error(f"💥 Cron service crashed: {str(e)}")
        exit(1)