from typing import Annotated

from pydantic import BaseModel

from simputils.config.generic import BasicConfigEnum
from simputils.config.models import AnnotatedConfigData


class MyModel0(BaseModel):
	sub1: str = None
	sub2: int = None
	sub3: float = None


class MyModel(BaseModel):
	field1: str = None
	field2: int = 34
	field3: float = None
	field4: list = [1, 2, ]
	field5: tuple = (1, 2, )
	field6: dict = None
	field7: MyModel0 = None


class MyConfigEnum(BasicConfigEnum):
	MODEL1: Annotated[str, AnnotatedConfigData(
		type=MyModel | None
	)] = "model1"
	MODEL2: Annotated[str, AnnotatedConfigData(
		type=MyModel | None
	)] = "model1"


data = [
	(
		{
			MyConfigEnum.MODEL1: MyModel(
				field1="PandaHugMonster",
				field2=900,
				field3=13.12,
				field4=(10, 20, 30),
				field5=(100, 200, 300),
				field6={
					"test1": "test1",
					"test2": "test2",
					"test3": "test3",
				},
				field7=MyModel0(
					sub1="gg-wp",
					sub3=-3.1415,
				),

			)
		},

		(
			{
				MyConfigEnum.MODEL1: MyModel(
					field4=(10, ),
					field5=(100, 200, ),
					field6={
						"test1": "test1",
						"test3": "test3",
					},
					field7=MyModel0(
						sub1="gg-wp",
					),

				)
			},
			{
				MyConfigEnum.MODEL1: MyModel(
					field1="PandaHugMonster",
					field2=900,
					field3=13.12,
					field4=(20, 30, ),
					field5=(300, ),
					field6={
						"test2": "test2",
					},
					field7=MyModel0(
						sub3=-3.1415,
					),
				)
			}
		)
	),


	(
		{
			MyConfigEnum.MODEL1: MyModel(
				field1="PandaHugMonster",
				field2=900,
				field3=13.12,
				field4=(10, 20, 30),
				field5=(100, 200, 300),
				field6={
					"test1": "test1",
					"test2": "test2",
					"test3": "test3",
				},
				field7=MyModel0(
					sub1="gg-wp",
					sub3=-3.1415,
				),

			)
		},

		(
			{
				MyConfigEnum.MODEL1: MyModel(
					field4=(10, ),
					field5=(100, 200, ),
					field6={
						"test1": "test1",
						"test3": "test3",
					},
				)
			},
			{
				MyConfigEnum.MODEL1: {
					"field1": "PandaHugMonster",
					"field2": 900,
					"field3": 13.12,
					"field4": (20, 30,),
					"field5": (300,),
					"field6": {
						"test2": "test2",
					},
					"field7": {
						"sub1": "gg-wp",
						"sub3": -3.1415,
					},
				}
			}
		)
	),


	(
		{
			MyConfigEnum.MODEL1: MyModel(
				field1="PandaHugMonster",
				field2=900,
				field3=13.12,
				field4=(10, 20, 30),
				field5=(100, 200, 300),
				field6={
					"test1": "test1",
					"test2": "test2",
					"test3": "HHH",
				},
				field7=MyModel0(
					sub1="gg-wp",
					sub3=-3.1415,
				),

			)
		},

		(
			{
				MyConfigEnum.MODEL1: MyModel(
					field4=(10, ),
					field5=(100, 200, ),
					field6={
						"test1": "test1",
						"test3": MyModel0(),
					},
				)
			},
			{
				MyConfigEnum.MODEL1: {
					"field1": "PandaHugMonster",
					"field2": 900,
					"field3": 13.12,
					"field4": (20, 30,),
					"field5": (300,),
					"field6": {
						"test2": "test2",
						"test3": "HHH",
					},
					"field7": {
						"sub1": "gg-wp",
						"sub3": -3.1415,
					},
				}
			}
		)
	),
]
