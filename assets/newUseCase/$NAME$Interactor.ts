import { Interactor } from '$CORE$/definitions/Interactor'
import { $NAME$Input } from './$NAME$Input'
import { $NAME$Output } from './$NAME$Output'
import { $NAME$Repository } from './$NAME$Repository'

export class $NAME$Interactor extends Interactor<$NAME$Input, $NAME$Output, $NAME$Repository> {
	constructor(repository: $NAME$Repository) {
		super(repository)
	}

	/**
	 * TODO Write documentation for $NAME$Interactor.execute()
	 * @param input
	 * @return {Promise.<$NAME$Output>}
	 * @throws
	 */
	async execute(input: $NAME$Input): Promise<$NAME$Output> {
		this.input = input

		
	}
}
