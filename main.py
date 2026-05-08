from fastmcp import FastMCP
from tools.resume_tools import resume_ats_optimizer_and_pdf_generator
import asyncio

mcp = FastMCP("Vrund's ResumeForge")

mcp.tool()(resume_ats_optimizer_and_pdf_generator)

async def main():
    await mcp.run_async(transport='http',host='0.0.0.0',port=8000)

if __name__ == "__main__":
    asyncio.run(main())