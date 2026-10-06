from abc import ABC, abstractmethod
from enum import Flag, auto

from app.models.job import Job


class ProviderCapability(Flag):
    SEARCH = auto()
    JOB_DETAILS = auto()
    EMPLOYER_BOARD = auto()


class JobProvider(ABC):
    name: str
    capabilities: ProviderCapability

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities


class SearchProvider(JobProvider):
    @abstractmethod
    def search(
        self,
        *,
        keywords: str,
        location: str | None = None,
    ) -> list[Job]:
        raise NotImplementedError


class EmployerBoardProvider(JobProvider):
    @abstractmethod
    def list_company_jobs(
        self,
        *,
        company_identifier: str,
    ) -> list[Job]:
        raise NotImplementedError


class JobDetailProvider(JobProvider):
    @abstractmethod
    def get_job(
        self,
        *,
        job_id: str,
    ) -> Job:
        raise NotImplementedError