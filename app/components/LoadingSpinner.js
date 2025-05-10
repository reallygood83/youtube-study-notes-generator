'use client';

// \) ¤< ôì¸
// x¸ İ1 | L ¬©ĞŒ ‘Åt Ä‰ „D Ü<\ \ÜiÈä.
export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center my-8">
      <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
      <p className="mt-4 text-gray-600">Yµ x¸| İ1Xà ˆµÈä.  ÜÌ 0ä$ü8”...</p>
      <p className="text-sm text-gray-500 mt-2">
        (Á 8tĞ 0| 30~2„ Ä Œ”   ˆµÈä)
      </p>
    </div>
  );
}