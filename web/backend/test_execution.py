#!/usr/bin/env python3
"""
Test Execution Module
Handles real-time execution of test plans with WebSocket support for live output streaming.
"""

import os
import sys
import json
import asyncio
import subprocess
import uuid
from datetime import datetime
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect

# Add parent directory to path to import existing framework modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class TestExecutionManager:
    """Manages test plan executions and WebSocket connections."""
    
    def __init__(self):
        self.active_executions: Dict[str, subprocess.Popen] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
    
    async def execute_test_plan(self, test_plan_id: str, websocket: WebSocket, debug_level: int = 0):
        """Execute a test plan and stream output via WebSocket."""
        execution_id = str(uuid.uuid4())
        
        try:
            # Register WebSocket connection
            self.websocket_connections[execution_id] = websocket
            
            # Get test plan file path
            test_plan_path = self._get_test_plan_path(test_plan_id)
            if not os.path.exists(test_plan_path):
                await self._send_error(websocket, f"Test plan not found: {test_plan_id}")
                return
            
            # Build command
            cmd = self._build_command(test_plan_path, debug_level)
            
            # Get project root directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            
            # Start execution
            await self._send_status(websocket, "STARTING", f"Starting execution of {test_plan_id}")
            
            # Execute the test plan from project root
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=project_root  # Execute from project root
            )
            
            self.active_executions[execution_id] = process
            
            await self._send_status(websocket, "RUNNING", "Test execution in progress")
            
            # Stream output in real-time
            await self._stream_output(process, websocket, execution_id)
            
            # Wait for completion
            return_code = process.wait()
            
            # Generate execution log
            log_filename = await self._generate_execution_log(
                test_plan_id, execution_id, return_code
            )
            
            if return_code == 0:
                await self._send_status(websocket, "COMPLETED", 
                                      f"Execution completed successfully. Log: {log_filename}")
                await self._send_execution_log_link(websocket, log_filename)
            else:
                await self._send_status(websocket, "FAILED", 
                                      f"Execution failed with return code {return_code}. Log: {log_filename}")
                await self._send_execution_log_link(websocket, log_filename)
                
        except Exception as e:
            await self._send_error(websocket, f"Execution error: {str(e)}")
        finally:
            # Cleanup
            self._cleanup_execution(execution_id)
    
    def _get_test_plan_path(self, test_plan_id: str) -> str:
        """Get the full path to a test plan file."""
        test_plans_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test_plans')
        return os.path.join(test_plans_dir, f"{test_plan_id}.json")
    
    def _build_command(self, test_plan_path: str, debug_level: int) -> list:
        """Build the command to execute main.py."""
        # Use absolute path to main.py from the project root
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        main_script = os.path.abspath(os.path.join(project_root, 'main.py'))
        
        # Use unbuffered output for real-time streaming
        cmd = [sys.executable, '-u', main_script, test_plan_path]
        
        if debug_level > 0:
            cmd.extend(['-d', str(debug_level)])
        
        return cmd
    
    async def _stream_output(self, process: subprocess.Popen, websocket: WebSocket, execution_id: str):
        """Stream stdout and stderr output via WebSocket in real-time."""
        try:
            # Create tasks for reading stdout and stderr concurrently
            stdout_task = asyncio.create_task(
                self._read_stream(process.stdout, websocket, "STDOUT")
            )
            stderr_task = asyncio.create_task(
                self._read_stream(process.stderr, websocket, "STDERR")
            )
            
            # Wait for both streams to complete
            await asyncio.gather(stdout_task, stderr_task)
                    
        except Exception as e:
            await self._send_error(websocket, f"Output streaming error: {str(e)}")
    
    async def _read_stream(self, stream, websocket: WebSocket, stream_type: str):
        """Read from a stream and send output via WebSocket."""
        try:
            while True:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, stream.readline
                )
                if not line:
                    break
                
                line = line.rstrip()
                if line:  # Only send non-empty lines
                    await self._send_output(websocket, stream_type, line)
                    
        except Exception as e:
            print(f"Error reading {stream_type}: {e}")
    
    async def _generate_execution_log(self, test_plan_id: str, execution_id: str, return_code: int) -> str:
        """Generate execution log file with consistent naming."""
        # Get test plan name for filename
        test_plan_path = self._get_test_plan_path(test_plan_id)
        with open(test_plan_path, 'r') as f:
            test_plan_data = json.load(f)
            test_plan_name = test_plan_data.get('name', test_plan_id)
        
        # Replace all spaces with underscores in test plan name
        test_plan_name_clean = test_plan_name.replace(' ', '_')
        
        # Create filename with consistent format (use underscores instead of spaces)
        now = datetime.now()
        filename = f"log_{test_plan_name_clean}_{now.strftime('%Y-%m-%d_%H_%M')}.json"
        
        # Don't create a basic log - let main.py create the detailed execution log
        # The main.py script will create the actual execution log with detailed results
        
        return filename
    
    async def _send_status(self, websocket: WebSocket, status: str, message: str):
        """Send execution status update."""
        await websocket.send_json({
            "type": "STATUS",
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _send_output(self, websocket: WebSocket, stream_type: str, line: str):
        """Send output line."""
        await websocket.send_json({
            "type": "OUTPUT",
            "stream": stream_type,
            "line": line,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _send_error(self, websocket: WebSocket, error_message: str):
        """Send error message."""
        await websocket.send_json({
            "type": "ERROR",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _send_execution_log_link(self, websocket: WebSocket, log_filename: str):
        """Send execution log link."""
        await websocket.send_json({
            "type": "LOG_LINK",
            "url": f"http://localhost:3000/#/execution-logs/{log_filename}",
            "filename": log_filename,
            "timestamp": datetime.now().isoformat()
        })
    
    def _cleanup_execution(self, execution_id: str):
        """Clean up execution resources."""
        if execution_id in self.active_executions:
            process = self.active_executions[execution_id]
            if process.poll() is None:
                process.terminate()
            del self.active_executions[execution_id]
        
        if execution_id in self.websocket_connections:
            del self.websocket_connections[execution_id]
    
    def stop_execution(self, execution_id: str):
        """Stop a running execution."""
        if execution_id in self.active_executions:
            process = self.active_executions[execution_id]
            if process.poll() is None:
                process.terminate()
            self._cleanup_execution(execution_id)


# Global instance
execution_manager = TestExecutionManager()
