"""
Base Service module
"""
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, delete as sql_delete
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.v1.users import User

ModelType = TypeVar("ModelType")
# Model could be User, Product, Room, Profile

async def validate_pagination(filterer: dict) -> tuple:
    """
    Validate page and limit from filter.
    """
    page = filterer.pop("page", 1)
    if page < 1:
        page = 1
    limit = filterer.pop("limit", 50)
    if limit < 1 or limit > 50:
        limit = 50

    return page, limit, filterer

async def validate_sort(model: Type[ModelType], sort: str) -> Optional[InstrumentedAttribute]:
    """
    Validate if the sort field exists on the model.
    :param filterer: dict containing the field name to order by
    :param model: the SQLAlchemy model class
    :return: the model attribute if valid, else None
    """
    if sort.startswith("-"):
        sort = sort.lstrip("-")
    if hasattr(model, sort):
        return getattr(model, sort)

async def validate_params(model: Type[ModelType], filterer: dict) -> dict:
    """
    Validate if the filterer fields exists on the model.
    :param filterer: dict containing the field name to order by
    :param model: the SQLAlchemy model class
    :return: the model attribute if valid, else None
    """
    return {k:v for k, v in filterer.items() if hasattr(model, k)}

            

class Service(Generic[ModelType]):
    """
    Base service class for all services
    """
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def create(self, schema: dict, session: AsyncSession) -> ModelType:
        """
        Create a new record in the database
        :param schema: dictionary containing model data
        :param session: AsyncSession from SQLAlchemy
        """
        if self.model == User:
            password = schema.pop("password", '')
            schema.pop("confirm_password", None)
            obj = self.model(**schema)
            obj.set_password(password)
        else:
            obj = self.model(**schema)

        session.add(obj)

        await session.commit()
        return obj

    async def fetch(self, filterer: dict, session: AsyncSession) -> Optional[ModelType]:
        """
        Fetch a record by using a passed filter(s)
        :param filterer: dictionary containing search data (e.g., {'id': 20})
        :param session: AsyncSession from SQLAlchemy
        """
        if not filterer:
            return
        stmt = select(self.model)
        valid_fields = await validate_params(self.model, filterer)
        if not valid_fields:
            return

        for key, value in valid_fields.items():
            stmt = stmt.where(
                getattr(self.model, key) == value
            )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def fetch_all(self, filterer: dict, session: AsyncSession) -> List[ModelType]:
        """
        Fetch all records with optional filters
        :param filter: dictionary containing filter parameters
        :param session: AsyncSession from SQLAlchemy
        """
        # validate pagination
        page, limit, filterer = await validate_pagination(filterer)

        sort: str = filterer.pop("sort", "created_at")
        sort_attr = await validate_sort(self.model, sort)
        
        stmt = select(self.model)
        # validate filters
        valid_fields: dict = await validate_params(self.model, filterer)
        # return empty list if filter is all invalid field
        if not valid_fields and filterer:
            return []
        # apply filters
        for key, value in valid_fields.items():
            stmt = stmt.where(
                getattr(self.model, key) == value
            )
        # check for sorting
        if sort.startswith("-"):
            result = await session.execute(
                stmt.order_by(desc(sort_attr)).limit(limit).offset((page - 1) * limit)
            )
        else:
            result = await session.execute(
                stmt.order_by(asc(sort_attr)).limit(limit).offset((page - 1) * limit)
            )

        all_objects = result.scalars().all()
        return all_objects

    async def delete(self, filterer: dict, session: AsyncSession) -> None:
        """
        Delete a record by using the passed filter(s)
        :param filterer: dictionary containing search data (e.g., {'id': 20})
        :param session: AsyncSession from SQLAlchemy
        """
        stmt = sql_delete(self.model)
        valid_fields = await validate_params(self.model, filterer)
        if not valid_fields and filterer:
            return
        for key, value in valid_fields.items():
            stmt = stmt.where(
                getattr(self.model, key) == value
            )

        await session.execute(stmt)

    async def delete_all(self, session: AsyncSession) -> None:
        """
        Delete all records
        :param session: AsyncSession from SQLAlchemy
        """
        stmt = sql_delete(self.model)

        await session.execute(stmt)


if __name__ == "__main__":
    pass
