/** Global definitions for development **/

// for style loader
declare module '*.css' {
  const styles: any;
  export = styles;
}

// Omit type https://github.com/Microsoft/TypeScript/issues/12215
type Diff<T extends string, U extends string> = ({ [P in T]: P } &
  { [P in U]: never } & { [x: string]: never })[T];
type Omit<T, K extends keyof T> = { [P in Diff<keyof T, K>]: T[P] };

type PartialPick<T, K extends keyof T> = Partial<T> & Pick<T, K>;
type sentence = {
  id: string;
  text: string;
  nounPhrases: string[];
  paragraphNumber: number;
};

// slatejs editor types
interface SlateSelection {
  object: string;
  anchorKey: string;
  anchorOffset: number;
  focusKey: string;
  focusOffset: number;
  isBackward: boolean;
  isFocused: boolean;
  marks?: any;
}
